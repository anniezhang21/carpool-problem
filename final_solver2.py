import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils
from tsp_helper import *
from student_utils import *

OUTPUT_FILENAME = "naive_output.txt"

"""
======================================================================
  Complete the following function.
======================================================================
"""

def solve(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, params=[]):
    """
    Write your algorithm here.
    Input:
        list_of_locations: A list of locations such that node i of the graph corresponds to name at index i of the list
        list_of_homes: A list of homes
        starting_car_location: The name of the starting location for the car
        adjacency_matrix: The adjacency matrix from the input file
    Output:
        A list of locations representing the car path
        A dictionary mapping drop-off location to a list of homes of TAs that got off at that particular location
        NOTE: both outputs should be in terms of indices not the names of the locations themselves
    """
    # Ensure that the starting location is at the start.
    homes_and_start = list_of_homes.copy()
    if starting_car_location not in list_of_homes:
        homes_and_start.insert(0, starting_car_location)
    else:
        homes_and_start.remove(starting_car_location)
        homes_and_start.insert(0, starting_car_location)

    # Initialize storage structs (see below)
    sp_lookup = {}
    only_tas_adjacency = []


    # Get shortest paths between all houses w. networkx
    G, error = adjacency_matrix_to_graph(adjacency_matrix)
    for i, home1 in enumerate(homes_and_start):
        home1_index = list_of_locations.index(home1)
        home1_row = []
        for j, home2 in enumerate(homes_and_start):
            if home1 == home2:
                home1_row.append(0)
                continue
            home2_index = list_of_locations.index(home2)
            sp = nx.shortest_path(G, source=home1_index, target=home2_index)
            cost = cost_of_path(sp, adjacency_matrix)
            # Construct lookup dict ((i, j), (A, ... , B))
            # i.e. ((int, int), (int, ..., int))
            sp_lookup[(i, j)] = (tuple(sp))

            home1_row.append(cost)
        # Create adjacency mtx of only TA homes and start, for use in ortools tsp solver
        only_tas_adjacency.append(home1_row)

    # Plus into tsp_solver, get back shortest tour of TA houses
    shortest_tour = get_tsp_result(only_tas_adjacency, 0)

    # Replace house paths w actual paths from dict
    car_tour = []
    is_start = True
    first_ind = 0
    for index in range(len(shortest_tour) - 1):
        i, j = shortest_tour[index], shortest_tour[index + 1]
        sp = sp_lookup[(i, j)]
        if is_start:
            first_ind = sp[0]
            is_start = False
        sp_without_last = sp[:len(sp_lookup[(i, j)]) - 1]
        for elem in sp_without_last:
            car_tour.append(elem)
    car_tour.append(first_ind)

    # Each TA gets dropped off at their house.
    dropoff_dict = {}
    for location_ind in car_tour:
        if list_of_locations[location_ind] in list_of_homes:
            dropoff_dict[location_ind] = [location_ind]

    # Replace any (A, B, A) pattern in the tour with just A, where B gets dropped off at A (if applicable)
    prev_prev_location = car_tour[0]
    prev_location = car_tour[1]
    new_tour = [prev_prev_location, prev_location]
    for location in car_tour[2:]:
        if location == prev_prev_location:
            # Detected (A, B, A) path, so delete the B (2nd A not yet added).
            print("detected there and back:", prev_prev_location, " ", prev_location, " ", location)
            new_tour = new_tour[:len(new_tour) - 1]

            # Remove B from the list of dropoff locations, Add B to A.
            del dropoff_dict[prev_location]
            if location in dropoff_dict:
                dropoff_dict[location].append(prev_location)
            else:
                dropoff_dict[location] = [prev_location]

        else:
            new_tour.append(location)
        prev_prev_location = prev_location
        prev_location = location

    # Done
    print(new_tour)
    print(dropoff_dict)
    return new_tour, dropoff_dict

""" Lookup in adj matrix the cost of some path"""
def cost_of_path(path, adj_matrix):
    total, start, next = 0, 0, 1
    while next < len(path):
        total += adj_matrix[path[start]][path[next]]
        start += 1
        next += 1
    return total

"""
======================================================================
   No need to change any code below this line
======================================================================
"""

"""
Convert solution with path and dropoff_mapping in terms of indices
and write solution output in terms of names to path_to_file + file_number + '.out'
"""
def convertToFile(path, dropoff_mapping, path_to_file, list_locs):
    string = ''
    for node in path:
        string += list_locs[node] + ' '
    string = string.strip()
    string += '\n'

    dropoffNumber = len(dropoff_mapping.keys())
    string += str(dropoffNumber) + '\n'
    for dropoff in dropoff_mapping.keys():
        strDrop = list_locs[dropoff] + ' '
        for node in dropoff_mapping[dropoff]:
            strDrop += list_locs[node] + ' '
        strDrop = strDrop.strip()
        strDrop += '\n'
        string += strDrop
    utils.write_to_file(path_to_file, string)

def solve_from_file(input_file, output_directory, params=[]):
    print('Processing', input_file)

    input_data = utils.read_file(input_file)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(input_data)
    car_path, drop_offs = solve(list_locations, list_houses, starting_car_location, adjacency_matrix, params=params)

    basename, filename = os.path.split(input_file)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = utils.input_to_output(input_file, output_directory)

    convertToFile(car_path, drop_offs, output_file, list_locations)


def solve_all(input_directory, output_directory, params=[]):
    input_files = utils.get_files_with_extension(input_directory, 'in')

    for input_file in input_files:
        solve_from_file(input_file, output_directory, params=params)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--all', action='store_true', help='If specified, the solver is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', type=str, help='The path to the input file or directory')
    parser.add_argument('output_directory', type=str, nargs='?', default='.', help='The path to the directory where the output should be written')
    parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    output_directory = args.output_directory
    if args.all:
        input_directory = args.input
        solve_all(input_directory, output_directory, params=args.params)
    else:
        input_file = args.input
        solve_from_file(input_file, output_directory, params=args.params)
