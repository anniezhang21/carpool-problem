import random
import string
from student_utils import *

NAME_LENGTH = 8 # number of characters in randomly generated location names.

TOTAL_LOCATIONS = 50  # total number of nodes in graph
TA_HOMES = 20 # number of homes in graph (must be strictly less than TOTAL_LOCATIONS)
LOCATION_NAMES = []
HOME_NAMES = []
INPUT_MATRIX = []

# Lower numbers = more edges, high numbers = less edges. Between 1-10, exclusive.
BRANCHING_FACTOR = 9.9 # 1 = fully connected, 10 = no edges.
# random.seed(17) # Use if deterministic outputs needed


"""
Generate the randomized location names and store the names as a list in LOCATION_NAMES and HOME_NAMES
"""
def generate_names():
    for _ in range(TOTAL_LOCATIONS):
        new_name = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(NAME_LENGTH)])
        LOCATION_NAMES.append(new_name)
    shuffled_locs = LOCATION_NAMES.copy()
    random.shuffle(shuffled_locs)
    for i in range(TA_HOMES):
        HOME_NAMES.append(shuffled_locs[i])

"""
Print the whole header.
"""
def print_header():
    print(TOTAL_LOCATIONS)
    print(TA_HOMES)
    print(" ".join(LOCATION_NAMES))
    print(" ".join(HOME_NAMES))
    print(LOCATION_NAMES[TOTAL_LOCATIONS-1]) # Using the last location as the start.


"""
Print some matrix in the way it's represented in the spec
"""
def print_matrix(matrix):
    for row in matrix:
        for elem in row:
            print(elem, end=" ")
        print()


"""
Write the matrix and headers to the file called FILENAME.
"""
def write_input(matrix, filename):
    f = open(filename, "w")
    f.write(str(TOTAL_LOCATIONS))
    f.close()

    f = open(filename, "a")
    f.write("\n" + str(TA_HOMES))
    f.write("\n" + " ".join(LOCATION_NAMES))
    f.write("\n" + " ".join(HOME_NAMES))
    f.write("\n" + LOCATION_NAMES[TOTAL_LOCATIONS - 1] + "\n")
    for row in matrix:
        for elem in row:
            f.write(str(elem) + " ")
        f.write("\n")

    f.close()

"""
Generate the overall input matrix and store in INPUT_MATRIX.
"""
def generate_matrix():
    # Initialize input matrix
    for j in range(TOTAL_LOCATIONS):
        # Put x's in the diagonal because a node cannot be conencted to itself.
        INPUT_MATRIX.append(['x' if i == j else 1 for i in range(TOTAL_LOCATIONS)])

    populate_randomly()
    while not validate_connected():
        populate_randomly()


"""
Populate matrix with garbage but ~~~symmetrically~~~ :D
"""
def populate_randomly():
    for j in range(len(INPUT_MATRIX)):
        for i in range(len(INPUT_MATRIX[j])):
            # Cannot connect a node to itself.
            if i == j:
                continue

            # Ensure symmetric matric
            if j > i:
                INPUT_MATRIX[j][i] = INPUT_MATRIX[i][j]

            # Randomly choose to add an edge (weight = distance) or not ('x').
            else:
                rand_num = random.randint(1, 10)
                if rand_num > BRANCHING_FACTOR:
                    INPUT_MATRIX[j][i] = abs(i - j) + float((i - j)/1000)
                else:
                    INPUT_MATRIX[j][i] = 'x'

"""
Return True or False depending on whether or not the matrix corresponds to a connected + metric graph.
"""
def validate_connected():
    # Stolen fron input_validator.py and student_utils.py
    adjacency_mtx = [[entry if entry == 'x' else float(entry) for entry in row] for row in INPUT_MATRIX]
    G, adj_message = adjacency_matrix_to_graph(adjacency_mtx)

    # if failed to create adjacency matrix, terminate
    if adj_message:
        print(adj_message)
        return None
    # if graph is not connected, return False
    if not nx.is_connected(G) or not is_metric(G):
        return False
    else:
        return True


def main():
    generate_names()
    generate_matrix()
    write_input(INPUT_MATRIX, "rand_input.txt")
    # print_header()
    # print_matrix(INPUT_MATRIX)


if __name__ == "__main__": main()

