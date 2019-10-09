#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from pyscipopt import Model

from collections import namedtuple

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def get_solution(model, var):
    print('solving')
    model.optimize()

    print(model.getVars(var['ywc']))

    return

def length(point1, point2):
    ''' Returns the euclidean distance between two points'''
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def build_distances_matrix(facilities, customers):
    d_m = [
      [ length(c.location, w.location) for w in facilities ]
      for c in customers
    ]
    # returns a matrix indexed like this:
    # d_m(c, w)
    return d_m

def build_model(facilities, customers, d_m):
    print(d_m)
    model = Model('Facility')

    xw = [ 
        model.addVar('x{}'.format(w.index), 
        vtype='BINARY') 
        for w in facilities
    ]
    
    ywc = [
        [model.addVar('y{}{}'.format(w.index, c.index), 
        vtype='BINARY')
        for w in facilities] for c in customers
    ]
    for c in ywc:
        model.addCons(sum(c)==1)

        for w in facilities:
          model.addCons(c[w.index]<=xw[w.index])

    l_w = len(facilities)
    l_c = len(customers)

    # TODO: Add constraints to dont allow to overhead the facility capacity
    # Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
    # Customer = namedtuple("Customer", ['index', 'demand', 'location'])


    # [ (d, ywc), ... ]
    obj_1 = [
        ( d_m[c_id][w_id], ywc[c_id][w_id] ) 
        for c_id in range(l_c) for w_id in range(l_w)
    ]

    obj_2 = [ 
        ( facilities[w_id].setup_cost, xw[w_id] ) 
        for w_id in range(l_w)
    ]
    print(obj_2)


    model.setObjective(sum([o[0]*o[1] for o in obj_1+obj_2]),
        sense = 'minimize',
        clear = 'true' 
    )	
    model.writeProblem('facility_model.lp')
    return model, {'xw': xw, 'ywc':ywc}

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

    d_m = build_distances_matrix(facilities, customers)
    facility_m, variables = build_model(facilities, customers, d_m)
    get_solution(facility_m, variables)

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

