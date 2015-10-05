import time
import partial
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import json
from networkx.readwrite import json_graph
import findspark
findspark.init("/home/zelong/spark")
import pyspark
sc = pyspark.SparkContext()
with open("graph/nc_mini.json", "r") as graph_data:
    graph_data = json.load(graph_data)
    NC_digraph = json_graph.node_link_graph(graph_data)
    
    
####################################################################################
nodes_set = NC_digraph.nodes()





def cascade(init_nodes, nodes_set_broadcast):#, dist_d):
    nodes_set = nodes_set_broadcast.value
    action = {}
    n = len(init_nodes)
    #np.random.seed(random_d)
    #init_nodes = np.random.choice(NC_digraph.nodes(), 1)[0]
    for i in init_nodes:
        action[i] = 1
    #st = set()
    #st.add(init_nodes)
    init_list = zip([0]*len(init_nodes),init_nodes[::])
    inter = 0
    while len(init_list) != 0 and inter <10 :
        curr_node = init_list.pop(0)
        #print curr_node
        for i in nodes_set[curr_node[1]]:
            if i not in action:
                b = nodes_set.node[i]['review_count']
                a =  nodes_set[curr_node[1]][i]['weight']
                #np.random.seed(12)
                b_dist = np.sqrt(np.random.beta(a = a, b = b))
                #np.random.seed(12)
                u_dist = np.random.uniform(0,1)
                if b_dist > u_dist:
                    action[i] = 1
                    #st.add(i)
                    inter = curr_node[0] + 1
                    init_list.append((inter, i))
                    n = n + 1

    return n

def influence_function(N, init_nodes, partition_num):
    nodes_set_broadcast = sc.broadcast(NC_digraph)
    activated_num_rdd = sc.parallelize([init_nodes]*N, partition_num)
    activated_num = activated_num_rdd.map(lambda x: cascade(x, nodes_set_broadcast)).reduce(lambda x, y: (x+y)/2.0)
    return activated_num

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

nodes_set = NC_digraph.nodes()
init_nodes = np.random.choice(NC_digraph.nodes(), 1)[0]
#print calculateSK(nodes_set, 200, 3)

