#!/usr/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
from multiprocessing import Pool

import math
from pyscipopt import Model

from collections import namedtuple

SCIP_STATUS_OPTIMAL = 'optimal'
SCIP_STATUS_TIMELIMIT = 'timelimit'
SCIP_STATUS_INFEASIBLE = 'infeasible'
SCIP_STATUS_UNBOUNDED = 'unbounded'

SCIP_STAGE_INIT         =  0        #< SCIP data structures are initialized, no problem exists
SCIP_STAGE_PROBLEM      =  1        #< the problem is being created and modified
SCIP_STAGE_TRANSFORMING =  2        #< the problem is being transformed into solving data space
SCIP_STAGE_TRANSFORMED  =  3        #< the problem was transformed into solving data space
SCIP_STAGE_INITPRESOLVE =  4        #< presolving is initialized
SCIP_STAGE_PRESOLVING   =  5        #< the problem is being presolved
SCIP_STAGE_EXITPRESOLVE =  6        #< presolving is exited
SCIP_STAGE_PRESOLVED    =  7        #< the problem was presolved
SCIP_STAGE_INITSOLVE    =  8        #< the solving process data is being initialized
SCIP_STAGE_SOLVING      =  9        #< the problem is being solved
SCIP_STAGE_SOLVED       = 10        #< the problem was solved
SCIP_STAGE_EXITSOLVE    = 11        #< the solving process data is being freed
SCIP_STAGE_FREETRANS    = 12        #< the transformed problem is being freed
SCIP_STAGE_FREE         = 13        #< SCIP data structures are being freed

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def optimize_function(model):
    model.optimize()

    status = model.getStatus()
    stage = model.getStage()

    if status != SCIP_STATUS_OPTIMAL and stage < SCIP_STAGE_EXITPRESOLVE:
        return get_trivial_solution(facilities, customers)

    if status == SCIP_STATUS_OPTIMAL:
        optimal = 1 
        obj = model.getObjVal()
    else:
        obj = model.getPrimalbound()
    
    try:
        best_solution = model.getBestSol()
    except:
        return None, None, None

    solution = [-1] * len(customers)
    for c in customers:
      for w in facilities:
          ywc = vars['ywc'][c.index][w.index]
          if best_solution[ywc] == 1:
              solution[c.index] = w.index

    return obj, solution, optimal

def get_solution(facilities, customers, model, vars):
    obj = None
    solution = None
    optimal = 0

    model.hideOutput() # silent/verbose mode
    model.setRealParam('limits/time', 180)
    # model.writeProblem('facility_model.lp')

    with Pool(processes=3) as pool:
        r1 = pool.apply_async(optimize_function, (model,))

        try:
            obj, solution, optimal = r1.get(1)
        except:
            pass    
    
    if solution == None:
        return get_trivial_solution(facilities, customers)
    
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
    # d_m(c, w)
    return d_m

def build_model(facilities, customers, d_m):
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

    # Not allow overheading the facility capacity
    for w in facilities:
        cw = w.capacity
        cons = [
            (customers[c.index].demand, ywc[c.index][w.index])
            for c in customers
        ]
        model.addCons(sum([c[0]*c[1] for c in cons]) <= cw)

    # [ (d, ywc), ... ]
    obj_1 = [
        ( d_m[c.index][w.index], ywc[c.index][w.index] ) 
        for c in customers for w in facilities
    ]

    obj_2 = [ 
        ( facilities[w.index].setup_cost, xw[w.index] ) 
        for w in facilities
    ]

    model.setObjective(sum([o[0]*o[1] for o in obj_1+obj_2]),
        sense = 'minimize',
        clear = 'true' 
    )	
    return model, {'xw': xw, 'ywc':ywc}

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
    facility_m, variables = build_model(facilities, customers, d_m)

    obj, solution, optimal = get_solution(facilities, customers, facility_m, variables)

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

