import findspark
import annealing_spark
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
#Greedy Algorithm Implementation
#
######################################################################################

def getMaxGreedy_2(nodes_set, N, curr_nodes):
    result = []
    max_node = None
    max_influence = 0
    for i in nodes_set:
        tmp = influence_function(N, curr_nodes + [i], 4)
        if tmp > max_influence:
            max_node = i
            max_influence = tmp
    return max_node


#N: number of runs N in mul_cascade
#K: number of initial nodes for influence maximization
def calculateSK(nodes_set, N, K):
    # Perform getMaxGreedy for three times to get the solution for S3
    opt = []
    curr_nodes = []
    for i in range(K):
        tmp = getMaxGreedy_2(nodes_set, N, curr_nodes)
        curr_nodes = curr_nodes + [tmp]
        nodes_set.remove(tmp)

    max_influence = influence_function(N, curr_nodes, 4)
    #print curr_nodes
    return (curr_nodes, max_influence)

#function to run multiple times of greedy algorithm
def run_greedy(nodes_set, N, num):
    result = []
    for i in xrange(num):
        nodes_test = nodes_set[::]
        result.append(calculateSK(nodes_test, N, 3)[1])
    #print result
    print np.min(result)/np.max(result)
    plt.plot(result)

run_greedy(nodes_set, 100, 100)

