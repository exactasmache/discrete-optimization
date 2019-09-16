import sys, getopt

import networkx as nx
import matplotlib.pyplot as plt
import warnings
from matplotlib.cbook.deprecation import MatplotlibDeprecationWarning
warnings.filterwarnings("ignore", category=MatplotlibDeprecationWarning)

import cplex
from cplex.exceptions import CplexError


# ----------------------------------------------------------------------------
# Initialize the problem data
# ----------------------------------------------------------------------------
def parse_input_data(filename):

    # number of vertices, number of edges
    # for each edge: the end vertices and the cost of the edge
    # number of vertices to be connected together
    # the vertex numbers for the vertices that are to be connected together
    G=nx.Graph()
    m = None
    T = []
    n_T = None

    with open(filename) as ifile:
        while True:
            # read line
            l = ifile.readline()
            if not l: break

            if m == None:
                l = l.split()
                n, m = int(l[0]), int(l[1])

            elif len(G.edges) < m:
                label = len(G.edges)
                l = l.split()
                G.add_edge(*l[:2], weight=int(l[2]), label=label)
            
            elif not n_T:
                n_T = int(l.strip())

            elif len(T) < n_T:
                labeled_T = l.split()
                # T = list(map(lambda x: int(x), labeled_T))
    
    return G, labeled_T


# ----------------------------------------------------------------------------
# Draw the solution as a graph
# ----------------------------------------------------------------------------
def draw_solution(G, T, S=None):
    pos = nx.spring_layout(G)

    not_S = list(set(G.edges()) - set(S))
    N = list(set(G.nodes()) - set(T))
    nx.draw_networkx_nodes(G, pos, nodelist=N, node_size=80)
    nx.draw_networkx_nodes(G, pos, nodelist=T, node_color='r', node_size=200)
    nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
    nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
    
    nx.draw_networkx_edges(G, pos, edgelist=S, width=2)
    nx.draw_networkx_edges(G, pos, edgelist=not_S, width=1, alpha=0.5, edge_color='b', style='dashed')
    plt.show()


# ----------------------------------------------------------------------------
# Build the model
# ----------------------------------------------------------------------------
def build_model(G, T):
    prob = cplex.Cplex()
    sorted_edges = sorted(G.edges(data=True), key=lambda x: x[2]['label'])
    sorted_nodes = sorted(G.nodes(data=True), key=lambda y: int(y[0]))
    obj = list(map(lambda e: e[2]['weight'], sorted_edges))

    x_names = list(map(lambda e: 'x_{}_{}'.format(e[0], e[1]), sorted_edges))
    y_names = list(map(lambda i: 'y{}'.format(i[0]), sorted_nodes))


    y_on_lh = []
    for i,j,dicc in sorted_edges:
        x = 'x_{}_{}'.format(i,j)
        constraint = [
          [['y{}'.format(i), 'x_{}_{}'.format(i,j)], [-1,1]],
          [['y{}'.format(j), 'x_{}_{}'.format(i,j)], [-1,1]]
        ]
        y_on_lh += constraint
    
    y_on_sign = 'L'*len(y_on_lh)
    y_on_rh = [0]*len(y_on_lh)
    prob.objective.set_sense(prob.objective.sense.minimize)
    prob.variables.add(obj=obj, names=x_names, 
                       types=[prob.variables.type.binary]*len(x_names))
    prob.variables.add(names=y_names, 
                       types=[prob.variables.type.binary]*len(y_names))

    prob.linear_constraints.add(lin_expr=y_on_lh, senses=y_on_sign, rhs=y_on_rh)

    return prob


def main(argv):
    inputfile = 'data/steinb1.txt'
    outputfile = 'solution.lp'
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('steiner.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
          print('steiner.py -i <inputfile> -o <outputfile>')
          sys.exit()
        elif opt in ("-i", "--ifile"):
          inputfile = arg
        elif opt in ("-o", "--ofile"):
          outputfile = arg
    return inputfile, outputfile

# ----------------------------------------------------------------------------
# Solve the model and display the result
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    inputfilename, outputfilename = main(sys.argv[1:])

    # Parse input data
    G, T = parse_input_data(inputfilename)
    
    
    # Build the model
    try:
      my_prob = build_model(G, T)
      my_prob.write(outputfilename)
      my_prob.solve()

    except CplexError as exc:
        print(exc)
        exit(1)
    
    numrows = my_prob.linear_constraints.get_num()
    numcols = my_prob.variables.get_num()

    print()
    # solution.get_status() returns an integer code
    print("Solution status = ", my_prob.solution.get_status(), ":", end=' ')
    # the following line prints the corresponding string
    print(my_prob.solution.status[my_prob.solution.get_status()])
    print("Solution value  = ", my_prob.solution.get_objective_value())
    # slack = my_prob.solution.get_linear_slacks()
    # pi = my_prob.solution.get_dual_values()
    # x = my_prob.solution.get_values()
    # dj = my_prob.solution.get_reduced_costs()
    # for i in range(numrows):
    #     print("Row %d:  Slack = %10f  Pi = %10f" % (i, slack[i], pi[i]))
    # for j in range(numcols):
    #     print("Column %d:  Value = %10f Reduced cost = %10f" %
    #           (j, x[j], dj[j]))
    
    # If G is small enough...
    # S = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 5]
    # draw_solution(G, T, S)
    

