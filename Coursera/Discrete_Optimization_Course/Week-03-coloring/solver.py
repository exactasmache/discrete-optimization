#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from ortools.sat.python import cp_model

# SOLVERS:
def solve(edges, node_count, model):
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    print('Solve status: %s' % solver.StatusName(status))
    if status == cp_model.OPTIMAL:
      print('Optimal objective value: %i' % solver.ObjectiveValue())
    
    print('Statistics')
    print('  - conflicts : %i' % solver.NumConflicts())
    print('  - branches  : %i' % solver.NumBranches())
    print('  - wall time : %f s' % solver.WallTime())
    # build a trivial solution
    # every node has its own color
    return range(0, node_count)

def get_colors_upper_bound(edges, n):
    # I can use the max degree.
    return n

def make_model(edges, n):
    # Model definition
    model = cp_model.CpModel()
    
    # Upper bound
    colors_upper_bound = get_colors_upper_bound(edges, n)
    
    # Variables: 
    # c_i = 3 iff the color 3 is assigned to the node i
    c = [ model.NewIntVar(0, colors_upper_bound-1, 
         'c_{}'.format(i)) for i in range(n)]
    # u_i = 1 iff the color i is used 
    # u = [ model.NewBoolVar('u_{}'.format(i)) 
    #       for i in range(colors_upper_bound)]
    
    target = model.NewIntVar(0, colors_upper_bound, 'obj')
    
    # Constraints: 
    # c_i != c_j for every ij in E
    for i,j in edges:
      model.Add(c[i] != c[j])
    
    model.AddMaxEquality(target, c)
    # u_i <= sum() #TODO
    # for i in range(colors_upper_bound):
    #   model.Add(c>0).OnlyEnforceIf(u[i])
    #   model.Add(c>0).OnlyEnforceIf(u[i].Not())


    # Objective function: minimize sum(u)
    # model.Minimize(sum(u))
    model.Minimize(target)
    return model

def prepare_return_data(solution, node_count, optimal=0):
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

    model = make_model(edges, node_count)
    
    solution = solve(model, edges, node_count)

    return prepare_return_data(solution, node_count)


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

