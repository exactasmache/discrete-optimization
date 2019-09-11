#!/usr/bin/python
# -*- coding: utf-8 -*-

# SOLVERS:
def trivialSolver(edges, node_count):
    # build a trivial solution
    # every node has its own color
    return range(0, node_count)


def prepareRetrunData(solution, node_count, optimal=0):
    # prepare the solution in the specified output format
    output_data = str(node_count) + ' ' + str(optimal) + '\n'
    output_data += ' '.join(map(str, solution))
    return output_data

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))


    if edge_count < 10 and node_count <10:
        solution = trivialSolver(edges, node_count)
    else:
        solution = trivialSolver(edges, node_count)


    return prepareRetrunData(solution, node_count)


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

