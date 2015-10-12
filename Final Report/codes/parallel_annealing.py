import findspark
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import json
from networkx.readwrite import json_graph
findspark.find()
findspark.init('/usr/local/opt/apache-spark/libexec')
import pyspark
import influence_function

sc = pyspark.SparkContext()

with open("graph/nc_mini.json", "r") as graph_data:
    graph_data = json.load(graph_data)
    NC_digraph = json_graph.node_link_graph(graph_data)

nodes_set = NC_digraph.nodes()


######################################################################################
#
#Simulated Annealing Algorithm Implementation
#
######################################################################################
def next_step(X, nodes_set_broadcast):
    tmp = nodes_set_broadcast.value[::]
    for i in X: tmp.remove(i)
    X[np.random.choice(range(len(X)))] = np.random.choice(tmp)
    return X

def simulated_annealing_rst(function, initial_X, initial_temp, cool, reanneal, iterr):

    accepted = 0
    X = initial_X.copy()
    T = initial_temp

    history = list()
    # Evaluate E
    prev_E = function(X)
    history.append(prev_E)

    for i in xrange(iterr):
        # Propose new path.
        X_star = changepath(X, 2)
        # Evaluate E
        new_E = function(X_star)
        delta_E = new_E - prev_E

        # Flip a coin
        U = np.random.uniform()
        if U < np.exp(-delta_E / T):
            accepted += 1
            history.append(new_E)
            # Copy X_star to X
            X = X_star.copy()
            prev_E = new_E

        # Check to cool down
        if accepted % reanneal == 0:
            T *= cool


# Simulated Annealing Parameters
initial_X = cities # Start random
initial_temp = 2.
cool = 0.9
reanneal = 100
iterr = 30000

N = 100
partition_num = 4

simulated_annealing_rst(lambda x: influence_function(N, x, partition_num), initial_X, initial_temp, cool, reanneal, iterr):

