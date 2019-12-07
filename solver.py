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
    # Create a new list of only TA homes and the start location, ensuring that the start location is at index 0.
    homes_and_start = list_of_homes.copy()
    if starting_car_location not in list_of_homes:
        homes_and_start.insert(0, starting_car_location)
    else:
        homes_and_start.remove(starting_car_location)
        homes_and_start.insert(0, starting_car_location)

    # # Get shortest paths between all pairs in start+homes w. networkx
    only_tas_adjacency, sp_lookup = \
        new_adj_matrix_with_lookup(homes_and_start, list_of_locations, adjacency_matrix)

    # Plus into tsp_solver, get back shortest tour of TA houses
    shortest_tour = get_tsp_result(only_tas_adjacency, 0) # 0 is index of where the car starts.

    # Replace house paths w actual paths from dict to get a valid car tour
    car_tour = get_valid_tour(shortest_tour, sp_lookup)
    print("original tour:", car_tour)


    # To start, each TA gets dropped off at their house.
    dropoff_dict = {}
    for location_ind in car_tour:
        if list_of_locations[location_ind] in list_of_homes:
            dropoff_dict[location_ind] = [location_ind]


    # Replace any (A, B, A) pattern in the tour with just A, where B gets dropped off at A (if applicable)
    # car_tour = remove_single_there_and_backs(car_tour, dropoff_dict)


    # Find all (A, B, ..., B, A) patterns, remove, and rehome displaced TAs
    pattern_found, start, end = detect_spindle(car_tour)
    while pattern_found and start != None and end != None:
        car_tour, next_start = handle_spindle(car_tour, start, end, dropoff_dict)
        pattern_found, local_start, local_end = detect_spindle(car_tour[next_start:])
        if pattern_found:
            start, end = local_start + next_start, local_end + next_start
        else:
            start, end = local_start, local_end

    # Done
    print(car_tour)
    print(dropoff_dict)
    return car_tour, dropoff_dict


"""
Create new adjacency matrix with only the locations specified and corresponding lookup dicts.
PARAMS: location_subset: Either a list of location names or location indexes
        all_locs: The list of all possible location names 
        global_adj_mtx: The adj matrix representing the orignal graph

RETURN: new_adjacency: new graph including only the location subset
        sp_lookup: convert from local index path to global sp
"""
def new_adj_matrix_with_lookup(location_subset, all_locs, global_adj_mtx):
    # Initialize storage structs (see below)
    new_adjacency = []
    sp_lookup = {}

    # Get shortest paths between all pairs locations in the subset w. networkx
    G, error = adjacency_matrix_to_graph(global_adj_mtx)
    for i, home1 in enumerate(location_subset):
        # Get global index and add entry to lookup dict
        if type(home1) == str:
            home1_index = all_locs.index(home1)
        else:
            home1_index = home1

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

    return new_adjacency, sp_lookup


""" Lookup in adj matrix the cost of some path"""
def cost_of_path(path, adj_matrix):
    total, start, next = 0, 0, 1
    while next < len(path):
        total += adj_matrix[path[start]][path[next]]
        start += 1
        next += 1
    return total


"""
Get a car tour by replacing values in the subset adjacency matrix with that of the global adj. matrix.
"""
def get_valid_tour(local_tour, lookup_dict):
    car_tour = []
    is_start = True
    first_ind = 0
    for index in range(len(local_tour) - 1):
        i, j = local_tour[index], local_tour[index + 1]
        sp = lookup_dict[(i, j)]
        if is_start:
            first_ind = sp[0]
            is_start = False
        sp_without_last = sp[:len(lookup_dict[(i, j)]) - 1]
        for elem in sp_without_last:
            car_tour.append(elem)
    car_tour.append(first_ind)
    return car_tour


"""
Postprocess the tsp tour by removing any patterns like (A, B, A) and replacing with just (A), where B gets
dropped off at A and walks the rest of the way

Return: new tour.
"""
def remove_single_there_and_backs(original_tour, dropoff_dict):
    prev_prev_location = original_tour[0]
    prev_location = original_tour[1]
    new_tour = [prev_prev_location, prev_location]
    for location in original_tour[2:]:
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
    return new_tour


"""
Detect the first "there and back" pattern in some input tour (list of ints).
RETURN: exists: Boolean: Was a pattern found or not?
        start_index: index at which the spindle starts.
        end_index: index at which the spindle ends.
"""
def detect_spindle(input_tour):
    exists = False
    start_ind = None
    end_ind = None
    if len(input_tour)< 2:
        return exists, start_ind, end_ind

    stack = [(0, input_tour[0])]
    next_to_push = (1, input_tour[1])

    for i, node in enumerate(input_tour):
        if not stack or i < 2:
            continue
        # Found a spindle
        if node == stack[len(stack) - 1][1]:
            first_appearance, _ = stack.pop()
            if not exists:
                start_ind = first_appearance
                end_ind = i
                exists = True
            else:
                start_ind -= 1
                end_ind += 1

        elif not exists:
            stack.append(next_to_push)
            next_to_push = (i, node)

        else:
            break
    return exists, start_ind, end_ind


"""
Given a car tour and start and stop indices of a spindle, remove the spindle, taking care to 
rehome TAs and modify the dropoff dict in place.

RETURN: the tour with the spindle removed and the index of where it was removed.
"""
def handle_spindle(car_tour, spindle_start, spindle_end, dropoff_dict):
    print("found a long spindle from {} to {},  pruning...".format(spindle_start, spindle_end))
    most_recently_seen_tas = None     # (node, [list of TAs], node_index)
    second_recently_seen_tas = None   # (node, [list of TAs], node_index)
    seen_tas = set()
    for i, node in enumerate(car_tour):
        if i < spindle_start:  # This is so hacky oof
            continue
        elif i > spindle_end:
            break
        if node in dropoff_dict and node not in seen_tas: #There are TAs here
            second_recently_seen_tas = most_recently_seen_tas
            most_recently_seen_tas = (node, dropoff_dict[node], i)
            seen_tas.add(node)

    # The spindle only contains 1 TA node (at the very end).
    if second_recently_seen_tas == None or second_recently_seen_tas[0] == spindle_end:
        pruned_tour = car_tour[:spindle_start] + car_tour[spindle_end:]
        stub_node = car_tour[spindle_end]
        if stub_node in dropoff_dict:
            dropoff_dict[stub_node] += most_recently_seen_tas[1]
        else:
            dropoff_dict[stub_node] = most_recently_seen_tas[1]
        del dropoff_dict[most_recently_seen_tas[0]]

        ind_to_continue_at = spindle_start

    # The spindle contains multiple TA nodes, so only prune up to the second deepest TA node.
    else:
        # Redraw spindle start and end to the second deepest TA node.
        print(most_recently_seen_tas)
        print(second_recently_seen_tas)
        new_start_ind = second_recently_seen_tas[2]
        new_start_node = car_tour[new_start_ind]
        new_end_ind = new_start_ind
        for i, node in enumerate(car_tour):
            if i <= new_start_ind:
                continue
            if node == new_start_node:
                new_end_ind = i
                break
        print("multiple TAs in this branch. pruning from {} to {}". format(new_start_ind, new_end_ind))

        ind_to_continue_at = new_start_ind
        pruned_tour = car_tour[:new_start_ind] + car_tour[new_end_ind:]
        stub_node = car_tour[new_end_ind]
        if stub_node in dropoff_dict:
            dropoff_dict[stub_node] += most_recently_seen_tas[1]
        else:
            dropoff_dict[stub_node] = most_recently_seen_tas[1]
        del dropoff_dict[most_recently_seen_tas[0]]

    print("pruned tour:", pruned_tour)
    return pruned_tour, ind_to_continue_at




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
