#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight', 'benefit'])

debug = True

def calculate_upperbound(items, K):
    value = 0
    optimal = 0
    weight = 0
    for i in range(len(items)):
        if weight + items[i].weight <= K:
            weight += items[i].weight
            value += items[i].value
        else:
            space = K - weight
            value = value + space*1.0/items[i].weight * items[i].value
            break
    return value

def fill_knapsack_greedy(items, capacity, amount_items=None):
    if amount_items is None:
      amount_items = len(items)
    
    # I order the values descendant by benefit
    # I don't need to break equalities. It's the same for me.
    value = 0
    weight = 0
    optimal = 0
    taken = [0 for j in xrange(amount_items)]

    for item in items:
        if weight + item.weight <= capacity:
            taken[item.index] = 1
            value += item.value
            weight += item.weight
    
    return value, taken, optimal

def fill_knapsack_heuristically(items, capacity):
    amount_items = len(items)
    
    # I order the values descendant by benefit
    # I don't need to break equalities. It's the same for me.
    items.sort(key=lambda item: item.benefit, reverse=True)
    
    # I remove elements heavier than the allowed capacity or 
    # those which their values overpass the upper_bound:
    upper_bound = calculate_upperbound(items, capacity)
    items = filter(lambda i: i.weight < capacity and i.value < upper_bound, items)
    # items = filter(lambda i: i.weight > capacity*.02 and i.weight < capacity*.98, items)
    
    value, taken, optimal = fill_knapsack_greedy(items, capacity, amount_items)

    return value, taken, optimal


def fill_knapsack_dinamically(items, capacity, amount_items=None):
    
    # I order the values descendant by benefit
    # I don't need to break equalities. It's the same for me.
    items.sort(key=lambda item: item.benefit, reverse=True)
    
    # I remember the amount of items, because I am going to remove some of them.
    if amount_items is None:
      amount_items = len(items)
    
    # I remove elements heavier than the allowed capacity:
    items = filter(lambda i: i.weight < capacity, items)

    # I need to fill the table recording the values I used in each column
    # For each item I have to decide for each capacity if I put it into the knapsack or not.
    # To decide that, I need to take a look at two cells: the left one, and the one located 
    # in the left column but size(i) rows up

    # Remember that in math notation the first index of a matrix 
    # indicates the row, and the second indicates the column.

    taken = [0 for j in xrange(amount_items)]
    values_table = [[0 for j in xrange(len(items)+1)] for i in xrange(capacity)]
    weights_table = [[0 for j in xrange(len(items)+1)] for i in xrange(capacity)]

    # for each item
    for i in xrange(1, len(items)+1):
      item_idx = i - 1
      item = items[item_idx]
      
      # for each capacity
      for c in xrange(1, capacity+1):
        c_idx = c-1
        
        # if the element doesn't fit into the knapsack
        if item.weight > c:
          values_table[c_idx][i] = values_table[c_idx][i-1]
          weights_table[c_idx][i] = weights_table[c_idx][i-1]
        
        # if there is space to put the element in the knapsack without modifying its items:
        elif c - weights_table[c_idx][i-1] >= item.weight:
            values_table[c_idx][i] = values_table[c_idx][i-1] + item.value
            weights_table[c_idx][i] = weights_table[c_idx][i-1] + item.weight
        
        #  if I can get a big value removing elements that allow me to put the actual
        else:
          if c_idx-item.weight <= 0:
            last_value = 0
            last_weight = 0
          else: 
            last_value = values_table[c_idx-item.weight][i-1]
            last_weight = weights_table[c_idx-item.weight][i-1]
          
          if values_table[c_idx][i-1] < last_value + item.value:
            values_table[c_idx][i] = last_value + item.value
            weights_table[c_idx][i] = last_weight + item.weight
          else:
            values_table[c_idx][i] = values_table[c_idx][i-1]
            weights_table[c_idx][i] = weights_table[c_idx][i-1]

    # For Debug purposes
    # print 'cap\t', [(i.weight, i.value) for i in items]
    # for j in xrange(capacity):
    #   print j+1, '\t',
    #   for i in xrange(len(items)+1):
    #     print values_table[j][i], '\t',
    #   print

    # Calculating the results
    max_c = capacity - 1
    max_i = len(items)
    max_value = values_table[max_c][max_i]
    max_weight = weights_table[max_c][max_i]
    optimal = 1
    i = max_i
    c = max_c
    if debug:
      calculated_weight = 0
      calculated_value = 0
    
    while i >= 0:
      while c >= 0:
        if values_table[c][i] != values_table[c][i-1]:
            if debug:
              calculated_weight += items[i-1].weight
              calculated_value += items[i-1].value
              item_idx = items[i-1].index
              # print 'estoy en la columna', i, 'que apunta al item', i-1, items[i-1]
            taken[item_idx] = 1
            c -= items[i-1].weight
        break
      i -= 1
    
    if debug:
      assert calculated_value == max_value
      assert calculated_weight == max_weight
      assert max_weight <= capacity

    return max_value, taken, optimal


def solve_it(input_data):
    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])
    
    items = []

    # We could sort the array here to improve computational average times but it is the same in terms of complexity.
    for i in xrange(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1]), float(parts[0])/int(parts[1])))

    # value, taken, optimal = fill_knapsack_greedy(items, capacity)
    if len(items)<=200:
        value, taken, optimal = fill_knapsack_dinamically(items, capacity)
    else :
        value, taken, optimal = fill_knapsack_heuristically(items, capacity)
        # value, taken, optimal = fill_knapsack_greedy(items, capacity)

    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(optimal) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

