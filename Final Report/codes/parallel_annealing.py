import findspark
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import json
from networkx.readwrite import json_graph
findspark.init('/usr/local/opt/apache-spark/libexec')
import pyspark
import influence_function
sc = pyspark.SparkContext()

# read graph
with open("graph/nc_mini.json", "r") as graph_data:
    graph_data = json.load(graph_data)
    NC_digraph = json_graph.node_link_graph(graph_data)


######################################################################################
#
#Influence Function Implementation
#
#######################################################################################

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
    activated_num = activated_num_rdd.map(lambda x: cascade(x, nodes_set_broadcast)).reduce(lambda x, y: x+y)
    return activated_num/N
####################################################################################


######################################################################################
#
#Simulated Annealing Algorithm Implementation
#
######################################################################################

def next_step(X, nodes_set):
    tmp = X[0]
    while tmp in X:
        tmp = np.random.choice(nodes_set)
    X[np.random.choice(range(len(X)))] = tmp
    return X


def simulated_annealing_rst(function, N, partition_num, initial_X, initial_temp, cool, reanneal, iterr, nodes_set):

    accepted = 0
    X = initial_X[::]
    T = initial_temp

    history = list()
    # Evaluate E
    prev_E = function(N, X, partition_num)
    history.append(prev_E)

    for i in xrange(iterr):
        # Propose new path.
        X_star = next_step(X, nodes_set)
        # Evaluate E
        new_E = function(N, X_star, partition_num)
        delta_E = new_E - prev_E

        # Flip a coin
        U = np.random.uniform()

        if U < np.exp(delta_E / T):
            accepted += 1
            history.append(new_E)
            print 'value:', new_E
            # Copy X_star to X
            X = X_star[::]
            print 'set:', X
            prev_E = new_E

        # Check to cool down
        if accepted % reanneal == 0:
            T *= cool

    return X, history

if __name__ == '__main__':

    # Simulated Annealing Parameters
    # initial_X = np.random.choice(NC_digraph.nodes(), 3, replace = False) # Start random
    initial_X = [u'emoQY8neOSJm-xwqh4xVfQ', u'-qffgThm1bv-URB0ndz0bA', u'zRIG4znrwIOp8mG4ZxtVMQ']

    initial_temp = 4.
    cool = 0.4
    reanneal = 100
    iterr = 10000
    N = 100
    partition_num = 4

    solution, history = simulated_annealing_rst(influence_function, N, partition_num, initial_X,
                                                initial_temp, cool, reanneal, iterr, NC_digraph.nodes())

    print "path:", solution
    print "length:", len(history)

    plt.figure(figsize=(12, 8))
    plt.plot(history)
    plt.title("History")
    plt.ylabel("$f(x_1,x_2)$",fontsize=12)
    plt.xlabel("Accepted", fontsize=12)
    plt.show()
