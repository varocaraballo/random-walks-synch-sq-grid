import grid_graph
import drones_team
import numpy as np
import sys
import pickle
from collections import deque


def checkConnectivity(initial_states, prev_initial_states):
    G = {i:set() for i in range(len(initial_states))}
    for i in range(len(initial_states)):
        for j in range(i+1, len(initial_states)):
            v = np.array(initial_states[i])
            pv = np.array(prev_initial_states[i])
            w = np.array(initial_states[j])
            pw = np.array(prev_initial_states[j])
            d = v - w
            pd = pv - pw
            if (d[0] == 0 and pd[0] == 0) or (d[1] == 0 and pd[1] == 0):
                G[i].add(j)
                G[j].add(i)
    marks = [False]*len(initial_states)
    q = deque()
    q.append(0)
    while len(q)>0:
        v = q.popleft()
        marks[v] = True
        for w in G[v]:
            if not marks[w]: q.append(w)
    return all(marks)
    

def broadcast_experiment(G, startingPositions, k, repetitions, protocol, max_iter, value4inf):
    bc = 0
    for i in range(repetitions):
        b_time = drones_team.broadcast_time(G, startingPositions, k, protocol, max_iter, checkConnectivity)
        if b_time == float('inf'):
            bc += value4inf
        else:
            bc += b_time
    return bc/repetitions


n = int(sys.argv[1])
protocol = int(sys.argv[2])
l = int(sys.argv[3])
G = grid_graph.diamondGridGraph(n,n)
startingPositions = [grid_graph.getStartVertexInDiamondGridGraph(i,j) for i in range(n) for j in range(n)]
ks = [i for i in range(2,n+1)]
d = [i for i in {int(n*n/j) for j in range(n-1,0,-1)}]
b = [int((d[i]+d[i+1])/2) for i in range(len(d)-1)]
ks = sorted(set(ks + d+b))
#ks = [i for i in range(2,int(n*n/9))]
#d = [i for i in range(int(n*n/9),n*n,5)]
#ks = sorted(set(ks + d+[n*n]))
broad_casts = np.array([(k, broadcast_experiment(G, startingPositions, k, int(5*n*n/k), protocol, 16*n*n if protocol != drones_team.PR_DETERMNISTIC else min(k*n, 2*n*n), 16*n*n)) for k in ks if k <= l])

#f = open("broadcast_{0}_{1}_{2}".format(n,n, 'random' if protocol == drones_team.PR_RANDOM else ('pseudo_random' if protocol == drones_team.PR_PSEUDO_RANDOM else 'deterministic')),"rb")
#old_data = pickle.load(f)
#f.close()
#
#for i in range(len(broad_casts)):
#    old_data[i] = (old_data[i]+broad_casts[i])/2

f = open("nnn_broadcast_{0}_{1}_{2}".format(n,n, 'random' if protocol == drones_team.PR_RANDOM else ('pseudo_random' if protocol == drones_team.PR_PSEUDO_RANDOM else 'deterministic')),"wb")
pickle.dump(broad_casts, f)
f.close()
