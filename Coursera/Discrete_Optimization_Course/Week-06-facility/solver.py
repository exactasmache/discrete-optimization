#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import cplex
import cplex.callbacks as cpx_cb
# from docplex.mp.model import Model

from collections import namedtuple

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])


def get_solution(facilities, customers, cpx, d_m):
    obj = None
    solution = None
    optimal = 0
    
    # CPLEX Parameters
    # cpx.write('facility_model.lp', filetype='lp')   # Write LP model to a file
    cpx.set_results_stream('output', fn=None)       # Hide output
    cpx.parameters.timelimit.set(180)               # Timelimit in seconds
    cpx.parameters.mip.tolerances.absmipgap.set(0)  # Absolute MIP gap tolerance
    cpx.parameters.mip.tolerances.mipgap.set(0)     # Relative MIP gap tolerance


    cpx.solve()
    status = cpx.solution.get_status_string()

    if 'no integer solution' in status:
        return get_trivial_solution(facilities, customers)
    
    # I asume that when the solution falls bellow the tolerance parameter it's optimal.
    if status == 'integer optimal solution':
        optimal = 1
      
    obj = cpx.solution.get_objective_value()
    
    # I think this returns the best bound, but without the integer solution
    # obj1 = cpx.solution.MIP.get_best_objective()
  
    # calc_objective = sum(
    #     [w.setup_cost * cpx.solution.get_values('x{}'.format(w.index)) for w in facilities]
    #     + 
    #     [d_m[c.index][w.index] * cpx.solution.get_values('y{}_{}'.format(w.index, c.index))
    #     for c in customers for w in facilities]
    # )
    # print(calc_objective)
    # with open('solution', 'w') as f:
    #     for n in cpx.variables.get_names():
    #         val = cpx.solution.get_values(n)
    #         rval = round(val)
    #         f.write('{} = {}     {}\n'.format(n, val, rval))

    solution = [-1] * len(customers)
    for c in customers:
        for w in facilities:
            if int(round(cpx.solution.get_values('y{}_{}'.format(w.index, c.index)))) == 1:
                solution[c.index] = w.index

    return obj, solution, optimal


def length(point1, point2):
    ''' Returns the euclidean distance between two points'''
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


def build_distances_matrix(facilities, customers):
    d_m = [
        [ length(c.location, w.location) for w in facilities ]
        for c in customers
    ]
    # it returns a matrix to be indexed as:
    # d_m[c][w]
    return d_m


def build_model(facilities, customers, d_m):
    cpx = cplex.Cplex()
    cpx.set_problem_name('Facility')

    # VARIABLES and OBJECTIVE FUNCTION
    xw = ['x{}'.format(w.index) for w in facilities]
    ywc = ['y{}_{}'.format(w.index, c.index) for c in customers for w in facilities]
    # ywc ˜= [[y0_0, ..., yn_0], [y0_1, ..., yn_1], ...]

    cpx.variables.add(obj = [w.setup_cost for w in facilities] 
                          + [d_m[c.index][w.index] for c in customers for w in facilities],
                      names = xw + ywc,
                      types=[cpx.variables.type.binary] * (len(xw)+len(ywc)))

    # CONSTRAINTS
    for c in customers:
        ind = ['y{}_{}'.format(w.index, c.index) for w in facilities]
        names = ['C_{}'.format(c.index)]
        val = [1.0] * len(facilities)
        rhs = [1.0]
        senses = ['E']
        cpx.linear_constraints.add(
            lin_expr = [ cplex.SparsePair(ind=ind, val=val) ],
            senses = senses,
            rhs = rhs,
            names = names,
        )

        names = ['W_{}_{}'.format(c.index, w.index) for w in facilities]
        senses = ['L'] * len(facilities)
        rhs = [0.0] * len(facilities)
        lin_exp = [ 
            cplex.SparsePair(
                ind=[ 'y{0}_{1}'.format(w.index, c.index), 
                      'x{0}'.format(w.index)], 
                val=[1, -1]
            ) for w in facilities 
        ]

        cpx.linear_constraints.add(
            lin_expr = lin_exp,
            senses = senses,
            rhs = rhs,
            names = names,
        )
    for w in facilities:
        ind = ['y{}_{}'.format(w.index, c.index) for c in customers]
        names = ['L_{}'.format(w.index)]
        val = [c.demand for c in customers]
        rhs = [w.capacity]
        senses = ['L']

        cpx.linear_constraints.add(
          lin_expr = [cplex.SparsePair(ind=ind, val=val)],
          senses = senses,
          rhs = rhs,
          names = names
        )

    return cpx

def parse_input(input_data):
    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    
    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))
    
    return facilities, customers

def get_trivial_solution(facilities, customers):
    # build a trivial solution
    # pack the facilities one by one until all the customers are served
    optimal = 0
    solution = [-1]*len(customers)
    capacity_remaining = [f.capacity for f in facilities]

    facility_index = 0
    for customer in customers:
        if capacity_remaining[facility_index] >= customer.demand:
            solution[customer.index] = facility_index
            capacity_remaining[facility_index] -= customer.demand
        else:
            facility_index += 1
            assert capacity_remaining[facility_index] >= customer.demand
            solution[customer.index] = facility_index
            capacity_remaining[facility_index] -= customer.demand

    used = [0]*len(facilities)
    for facility_index in solution:
        used[facility_index] = 1

    # calculate the cost of the solution
    obj = sum([f.setup_cost*used[f.index] for f in facilities])
    for customer in customers:
        obj += length(customer.location, facilities[solution[customer.index]].location)

    return obj, solution, optimal


def format_solution(obj, solution, optimal):
    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(optimal) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


def solve_it(input_data):
    facilities, customers = parse_input(input_data)
    
    d_m = build_distances_matrix(facilities, customers)
    facility_m = build_model(facilities, customers, d_m)

    if len(customers) > 1000:
        obj, solution, optimal = get_trivial_solution(facilities, customers)
    else:
        obj, solution, optimal = get_solution(facilities, customers, facility_m, d_m)

    return format_solution(obj, solution, optimal)


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')

