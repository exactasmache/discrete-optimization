#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from ortools.sat.python import cp_model

class StoreBestObjectiveSolution(cp_model.CpSolverSolutionCallback):
    """Store best intermediate solution."""
  
    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables['c']
        self.__best_objective = None
        self.__best_solution = None

    def on_solution_callback(self):
        if self.__best_objective == None or self.ObjectiveValue() > self.__best_objective:
            self.__best_objective = self.ObjectiveValue()
            self.__best_solution = [self.Value(v) for v in self.__variables]

    def get_best_solution(self):
        return {
          'obj': self.__best_objective, 
          'values': self.__best_solution
        }


def solve(model, variables, max_time=60.0):
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time
    solution = StoreBestObjectiveSolution(variables)

    status = solver.SolveWithSolutionCallback(model, solution)

    if status == cp_model.OPTIMAL:
        return {
          'obj': solver.ObjectiveValue(),
          'values': [ solver.Value(v) for v in variables['c']]
        }, 1
    else:
        return solution.get_best_solution(), 0

def get_grades(edges, n):
    grade = [0 for v in range(n)]
    for i,j in edges:
        grade[i] += 1
        grade[j] += 1
    return grade

def get_unconnected_nodes(G):
    return [n for n in G['N'] if G['g:N->int'][n] == 0]

def get_leaves(G):
    return [n for n in G['N'] if G['g:N->int'][n] == 1]

def find_cliques():
    return


def make_model(G):
    edges = G['E']
    nodes = G['N']
    grades = G['g:N->int']

    n = len(nodes)

    # Model definition
    model = cp_model.CpModel()
    
    # Domains
    unconnected = get_unconnected_nodes(G)
    leaves = get_leaves(G)

    # Upper bound
    UPPER = max(grades)-1
    u_bs = [0 if i in unconnected else (1 if i in leaves else UPPER) for i in nodes]
    obj_bound = max(u_bs)

    print(u_bs)
    # Variables: 
    # c_i = j iff the color j is assigned to the node i
    c = [ model.NewIntVar(0, u_bs[i], 
         'c_{}'.format(i)) for i in nodes]
    
    # target is the objective function
    target = model.NewIntVar(0, obj_bound, 'obj')

    # Constraints: 
    # c_i != c_j for every ij in E
    for i,j in edges:
      model.Add(c[i] != c[j])
    
    # target = max(c_i)
    model.AddMaxEquality(target, c)
    

    # Objective function: minimize max(c)
    model.Minimize(target+1)

    return model, {'c': c, 'obj': target}


def prepare_return_data(solution, optimal=0):
    # prepare the solution in the specified output format
    output_data = str(int(solution['obj'])) + ' ' + str(optimal) + '\n'
    output_data += ' '.join(map(str, solution['values']))
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
    
    G = {
      'N': range(node_count),
      'E': edges,
      'g:N->int': get_grades(edges, node_count)
    }
    model, variables = make_model(G)
    
    solution, optimal = solve(model, variables)

    return prepare_return_data(solution, optimal)


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

