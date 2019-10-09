#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import cplex
import cplex.callbacks as cpx_cb
from docplex.mp.model import Model

from collections import namedtuple

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def get_solution(cpx):
    print('solving')
    # print(cpx.problem_type[cpx.get_problem_type()])
    cpx.write('facility_model.lp', filetype='lp')
    # cpx.set_results_stream('output', fn=None)

    cpx.parameters.tune.timelimit.set(2)

    cpx.solve()
    
    optimal = False
    obj = None
    values = None
    
    status = cpx.solution.get_status_string()
    if status == 'integer optimal solution':
      optimal = True
      obj = cpx.solution.get_objective_value()
      y_values = cpx.solution.get_values()
    else:
      optimal = False
      obj = cpx.solution.MIP.get_best_objective()
      values = [] #TODO
    
    return obj, values

def length(point1, point2):
    ''' Returns the euclidean distance between two points'''
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def build_model(facilities, customers):
    xw = ['x{}'.format(w.index) for w in facilities]
    ywc = ['y{}{}'.format(w.index, c.index) for w in facilities for c in customers]

    cpx = cplex.Cplex()
    cpx.set_problem_name('Facility')

    cpx.variables.add(
        names = xw+ywc, 
        types=[cpx.variables.type.binary] * (len(xw)+len(ywc))
    )

    for c in customers:
        ind = ['y{}{}'.format(w.index, c.index) for w in facilities]
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

        names = ['W_{}{}'.format(c.index, w.index) for w in facilities]
        senses = ['L'] * len(facilities)
        rhs = [0.0] * len(facilities)
        lin_exp = [ 
            cplex.SparsePair(
                ind=[ 'y{0}{1}'.format(w.index, c.index), 
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
    
    return cpx

def solve_it(input_data):
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

    facility_m = build_model(facilities, customers)
    get_solution(facility_m)

    # build a trivial solution
    # pack the facilities one by one until all the customers are served
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

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


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

