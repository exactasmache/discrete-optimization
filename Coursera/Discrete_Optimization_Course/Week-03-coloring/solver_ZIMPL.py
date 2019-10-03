#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess

# SOLVERS:
def trivial_solver(edges, node_count):
    # build a trivial solution
    # every node has its own color
    return range(0, node_count)

def make_ZIMPL_model(edges, n, model_fn):
    nodes = map(lambda v: '"{}"'.format(v), range(0, n))
    arcs = map(lambda e: '<"{}","{}">'.format(e[0], e[1]), edges)
    with open(model_fn, 'w') as fn:
      fn.write('set N := {{{}}};\n'.format(','.join(nodes)))
      fn.write('set E := {{{}}};\n'.format(','.join(arcs)))
      fn.write('\n')
      fn.write('var c[N] integer;\n\n')
      fn.write('minimize colors: sum<i> in N: c[i];\n\n')
      fn.write('subto alldiff:\n')
      fn.write('forall <i,j> in E:\n')
      fn.write('c[i] != c[j];')

    return

def make_LP_model(zimpl_filename, lp_filename):
    commands = ' '.join([
      'zimpl',
      '-o {}'.format(lp_filename, ),
      '-t lp {}'.format(zimpl_filename, )
    ])
    print(commands)
    with open(os.devnull, 'w')  as FNULL:
        try:
            p = subprocess.check_call(commands, stdout=FNULL, shell=True)
        except subprocess.CalledProcessError as e:
            print('ERROR', e)

    return


def SCIP_solver(in_filename, sol_filename):
    commands = ' '.join([
      'scip',
      '-c "read {}"'.format(in_filename, ),
      '-c "optimize"',
      '-c "display solution"',
      '-c "write solution {}"'.format(sol_filename,),
      '-c "q"'
    ])
    print(commands)
    with open(os.devnull, 'w')  as FNULL:
        try:
            p = subprocess.check_call(commands, stdout=FNULL, shell=True)
        except subprocess.CalledProcessError as e:
            print('ERROR', e)

    return

def parse_solution(filename):
    # with open(filename, 'r') as fn:
    #   for l 
    return



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

    id = '{}_{}'.format(node_count, edge_count)
    zimpl_model_fn = 'model_{}.zpl'.format(id)
    lp_filename = '{}.lp'.format(id)
    sol_filename = '{}.sol'.format(id)
    
    make_ZIMPL_model(edges, node_count, zimpl_model_fn)
    make_LP_model(zimpl_model_fn, lp_filename)
    # SCIP_solver(lp_filename, sol_filename)
    # parse_solution(sol_filename)

    solution = trivial_solver(edges, node_count)

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

