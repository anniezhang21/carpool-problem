import numpy as np
import utils
from student_utils import *
from sklearn.cluster import KMeans

INPUT_FILE = "rand_input.txt"
MIN_CLUSTERS = 0.5 # want at least 50% of input size of clusters

"""
Return k clusters of nodes for some graph (represented as an adjacency matrix).

return: list[int] where the node at index i is classified into the result[i]-th cluster
"""
def k_clusters(k, adj_matrix):
    # Convert adj_matrix to numpy matrix
    adj_mtx = []
    for row in adj_matrix:
        adj_mtx.append(np.array(row))
    adj_mtx = np.array(adj_mtx)

    # Create the diagonal "degree matrix" i.e. sum of all edges into a node for all nodes.
    deg_mtx = np.diag(adj_mtx.sum(axis=1))

    # Calculate Laplacian matrix (???)
    laplacian = deg_mtx - adj_mtx

    # Get eigenvalues and eigenvectors
    vals, vecs = np.linalg.eig(laplacian)

    # Sort these based on the eigenvalues
    vecs = vecs[:, np.argsort(vals)]
    vals = vals[np.argsort(vals)]

    # Kmeans on first k vectors with nonzero eigenvalues
    first_nonzero = 0
    for val, vec in zip(vals, vecs):
        if val == 0:
            first_nonzero += 1
        else:
            break

    kmeans = KMeans(n_clusters=k + first_nonzero)
    kmeans.fit(vecs[:,first_nonzero:k])
    return kmeans.labels_


"""
Stolen from the internet.
"""
def original_example():
    A = np.array([
        [0, 1, 1, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0]])
    D = np.diag(A.sum(axis=1))
    laplacian= D - A

    # eigenvalues and eigenvectors
    vals, vecs = np.linalg.eig(laplacian)

    # sort these based on the eigenvalues
    vecs = vecs[:, np.argsort(vals)]
    vals = vals[np.argsort(vals)]

    kmeans = KMeans(n_clusters=4)
    kmeans.fit(vecs[:, 1:4])
    colors = kmeans.labels_

    print("Clusters:", colors)


"""
Takes the adjacency matrix and loads it into correct format for ortools tsp solver.
"""
def load_distance_from_file(input_file):
    _, _, _, _, _, adjacency_matrix = data_parser(utils.read_file(input_file))
    result = []
    for row in adjacency_matrix:
        result.append([0 if elem == 'x' else elem for elem in row])
    return result



def main():
    adj_matrix = load_distance_from_file(INPUT_FILE)
    start = int(MIN_CLUSTERS * len(adj_matrix))
    end = len(adj_matrix) + 1
    for i in range(start, end):
        print(k_clusters(i, adj_matrix))


if __name__ == '__main__':
    main()
