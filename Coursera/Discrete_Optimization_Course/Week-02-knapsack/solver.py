#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight', 'benefit'])

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

def fill_knapsack_groovy(items, capacity):
    # I order the values descendant by benefit
    # I don't need to break equalities. It's the same for me.
    value = 0
    weight = 0
    taken = [0]*len(items)

    for item in items:
        if weight + item.weight <= capacity:
            taken[item.index] = 1
            value += item.value
            weight += item.weight
    
    return value, taken, optimal

def fill_knapsack_dinamically(items, capacity):
    # I order the values descendant by benefit
    # I don't need to break equalities. It's the same for me.
    items.sort(key=lambda item: item.benefit, reverse=True)
    min_value_item = min(items, key= lambda item: item.value)
    min_weight_item = min(items, key= lambda item: item.weight)
    max_benefit_item = max(items, key= lambda item: item.benefit)
    max_weight_item = max(items, key= lambda item: item.weight)
    max_value_item = max(items, key= lambda item: item.value)
    
    # upper_bound = calculate_upperbound(items, capacity)
    # print capacity
    # print upper_bound
    # print min_value_item
    # print min_weight_item
    # print max_value_item
    # print max_weight_item
    # print max_benefit_item

    # I need to fill the table recording the values I used in each column
    # For each item I have to decide for each capacity if I put it into the knapsack or not.
    # If I do, I have to increment the value of all the elements of the column,

    capacities_items_table = []
    for item in items:
      print item


    value = 0
    optimal = 0
    weight = 0
    taken = [0]*len(items)
    
    for item in items:
        if weight + item.weight <= capacity:
            taken[item.index] = 1
            value += item.value
            weight += item.weight
    
    return value, taken, optimal

def solve_it(input_data):
    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])
    
    items = []

    # We could sort the array here to improve computational average times but it is the same in terms of complexity.
    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1]), float(parts[0])/int(parts[1])))

    # value, taken, optimal = fill_knapsack_groovy(items, capacity)
    value, taken, optimal = fill_knapsack_dinamically(items, capacity)
    
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

