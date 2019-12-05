import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import operator
import math
import utils
from tsp_helper import *
from student_utils import *
from clustering_helper import *

OUTPUT_FILENAME = "final1_output.txt"

MIN_CLUSTER_PERCENTAGE = 0.7

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
    best_cost = math.inf
    tour_with_best_cost = []
    dropoffs_of_tour_with_best_cost = {}

    # Index of starting car location and graph from nx
    start_ind = list_of_locations.index(starting_car_location)
    G, error = adjacency_matrix_to_graph(adjacency_matrix)

    # Construct new graph with only TA homes and start, for use in clustering.
    homes_and_start = list_of_homes.copy()
    homes_and_start.append(starting_car_location)
    only_tas_adjacency, _, only_tas_ind_lookup= \
        new_adj_matrix_with_lookups(homes_and_start, list_of_locations, adjacency_matrix)

    # Run tsp for many different possible clusters
    for k in range(len(list_of_homes), int(MIN_CLUSTER_PERCENTAGE * len(list_of_homes)), -1):
        clusters = k_clusters(k, only_tas_adjacency)

        # Create dict to map each cluster ID with the global indices of locs in that cluster.
        # i.e. (cluster ID: [locs_in_cluster])
        cluster_lookup = {}
        # Get home index in global adjacency list and add entry to cluster lookup
        for i in range(len(clusters)):
            actual_index = only_tas_ind_lookup[i]
            c_id = clusters[i]
            if c_id in cluster_lookup.keys():
                cluster_lookup[c_id].append(actual_index)
            else:
                cluster_lookup[c_id] = [actual_index]

        # Determine dropoff point for each cluster (global indexes). Create dict of (dropoff loc: people walking).
        dropoff_people_dict = {}
        global_dropoffs = [start_ind]
        for _, locs in cluster_lookup.items():
            dists_to_start = {}
            for loc in locs:
                if loc == start_ind:
                    dists_to_start[loc] = 0
                    continue
                this_dist = cost_of_path(nx.shortest_path(G, source=start_ind, target=loc), adjacency_matrix)
                dists_to_start[loc] = this_dist
            closest_loc = min(dists_to_start.items(), key=operator.itemgetter(1))[0]
            if closest_loc != start_ind:
                global_dropoffs.append(closest_loc)
            if closest_loc in dropoff_people_dict:
                continue
            dropoff_people_dict[closest_loc] = locs

        # Get adj matrix of only dropoff locations + start
        dropoffs_adj, dropoffs_sp_lookup, _ = \
            new_adj_matrix_with_lookups(global_dropoffs, list_of_locations, adjacency_matrix)

        # Plug into tsp_solver, get back shortest tour of dropoffs
        depot = 0  # Alg designed so that 0 is always the start.
        shortest_local_tour = get_tsp_result(dropoffs_adj, depot)

        # Replace house paths w actual paths from dict
        car_tour = []
        is_start = True
        first_ind = 0
        for index in range(len(shortest_local_tour) - 1):
            i, j = shortest_local_tour[index], shortest_local_tour[index + 1]
            sp = dropoffs_sp_lookup[(i, j)]
            if is_start:
                first_ind = sp[0]
                is_start = False
            sp_without_last = sp[:len(dropoffs_sp_lookup[(i, j)]) - 1]
            for elem in sp_without_last:
                car_tour.append(elem)
        car_tour.append(first_ind)

        # Everyone in each cluster gets dropped off at the closest point.
        final_dropoff_dict = {}
        for location_ind in car_tour:
            if location_ind in global_dropoffs:
                final_dropoff_dict[location_ind] = dropoff_people_dict[location_ind].copy()

        # Get cost of this car tour from output_generator.py. Keep track of best so far.
        tour_cost, _ = cost_of_solution(G, car_tour, final_dropoff_dict)
        if tour_cost < best_cost:
            print("best num clusters so far:", k)
            print("best cost so far:", tour_cost)
            best_cost = tour_cost
            tour_with_best_cost = car_tour
            dropoffs_of_tour_with_best_cost = final_dropoff_dict
        else:
            print("worse cluster: ", k, "(cost:", tour_cost, ")")

    # Return the tour with minimal cost.
    print(tour_with_best_cost)
    print(dropoffs_of_tour_with_best_cost)
    return tour_with_best_cost, dropoffs_of_tour_with_best_cost

"""
Create new adjacency matrix with only the locations specified and corresponding lookup dicts.
PARAMS: location_subset: Either a list of location names or location indexes
        all_locs: The list of all possible location names 
        global_adj_mtx: The adj matrix representing the orignal graph

RETURN: new_adjacency: new graph including only the location subset
        sp_lookup: convert from local index path to global sp
        ind_lookup: convert from local index to global index
"""
def new_adj_matrix_with_lookups(location_subset, all_locs, global_adj_mtx):
    # Initialize storage structs (see below)
    new_adjacency = []
    sp_lookup = {}
    ind_lookup = {}

    # Get shortest paths between all dropoff locations  w. networkx
    G, error = adjacency_matrix_to_graph(global_adj_mtx)
    for i, home1 in enumerate(location_subset):
        # Get global index and add entry to lookup dict
        if type(home1) == str:
            home1_index = all_locs.index(home1)
        else:
            home1_index = home1
        ind_lookup[i] = home1_index

        # Construct new adj matrix and populate sp lookup dict
        home1_row = []
        for j, home2 in enumerate(location_subset):
            if home1 == home2:
                home1_row.append(0)
                continue
            if type(home2) == str:
                home2_index = all_locs.index(home2)
            else:
                home2_index = home2
            sp = nx.shortest_path(G, source=home1_index, target=home2_index)
            cost = cost_of_path(sp, global_adj_mtx)
            # Construct lookup dict ((i, j): (A, ... , B))
            # i,e. (local indexes: sp b/t global indexes)
            # i.e. ((int, int): (int, ..., int))
            sp_lookup[(i, j)] = tuple(sp)
            home1_row.append(cost)

        # Create adjacency mtx of only TA homes, for use in ortools tsp solver
        new_adjacency.append(home1_row)

    return new_adjacency, sp_lookup, ind_lookup


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

    output_file = f'{output_directory}/{OUTPUT_FILENAME}'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

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
