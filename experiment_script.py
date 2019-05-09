# -*- coding: utf-8 -*-
import grid_graph
import drones_team
import pickle
import random
import sys

def experiment(G, startingPositions, k, steps, repetitions, protocol, arcsToStudy=None ):
    sum_avg_idle = 0
    sum_min_isol = 0
    sum_avg_isol = 0
    sum_max_isol = 0
    sum_studied_arcs_data = {}
    if arcsToStudy is not None:
        for arc in arcsToStudy:
            sum_studied_arcs_data[arc] = {}
    
    arcs_avg_idle_data = {}
    
    for i in range(repetitions):        
        (avg_idle, arcs_idle_data, min_isol, avg_isol, max_isol), studied_arcs_data = drones_team.simula(G, startingPositions, k, steps, protocol = protocol, arcsToStudy=arcsToStudy)
        sum_avg_idle += avg_idle
        sum_min_isol += min_isol
        sum_avg_isol += avg_isol
        sum_max_isol += max_isol
        for arc in studied_arcs_data:
            for v in studied_arcs_data[arc]:
                sum_studied_arcs_data[arc].setdefault(v,0)
                sum_studied_arcs_data[arc][v] += studied_arcs_data[arc][v]
        
        for arc in arcs_idle_data:
            arcs_avg_idle_data.setdefault(arc, 0)
            arcs_avg_idle_data[arc] += arcs_idle_data[arc]
            #arcs_avg_idle_data[arc] = max(arcs_idle_data[arc], arcs_avg_idle_data[arc]) if protocol == drones_team.PR_DETERMNISTIC else (arcs_idle_data[arc] + arcs_avg_idle_data[arc])
        
    min_idle_arc = float('inf')
    max_idle_arc = -1 
    for arc in arcs_avg_idle_data:
        min_idle_arc = min(min_idle_arc, arcs_avg_idle_data[arc]/repetitions)
        max_idle_arc = max(max_idle_arc, arcs_avg_idle_data[arc]/repetitions)
        #min_idle_arc = min(min_idle_arc, arcs_avg_idle_data[arc] if protocol == drones_team.PR_DETERMNISTIC else arcs_avg_idle_data[arc]/repetitions)
        #max_idle_arc = max(max_idle_arc, arcs_avg_idle_data[arc] if protocol == drones_team.PR_DETERMNISTIC else arcs_avg_idle_data[arc]/repetitions)
    
    return (min_idle_arc, sum_avg_idle/repetitions, max_idle_arc,           
            sum_min_isol/repetitions, sum_avg_isol/repetitions, sum_max_isol/repetitions), sum_studied_arcs_data
        

n = int(sys.argv[1])
protocol = int(sys.argv[2])
limit  = int(sys.argv[3])
arcsCount = 2
G = grid_graph.diamondGridGraph(n,n)
vertices = random.choices([i for i in G.keys()],k=arcsCount)
arcsToStudy = set()
for v in vertices:
    w = random.choice(G[v])
    arcsToStudy.add((v,w))
startingPositions = [grid_graph.getStartVertexInDiamondGridGraph(i,j) for i in range(n) for j in range(n)]
repetitions = 10
steps = 16*n*n



ks = [i for i in range(1,n+1)]
d = [i for i in {int(n*n/j) for j in range(n-1,0,-1)}]
d.sort()
ks = ks + d


statistics = [(k, experiment(G, startingPositions, k, steps, repetitions, protocol=protocol, arcsToStudy=arcsToStudy )) for k in ks if k <= limit]

f = open("{0}_{1}_{2}_{3}".format(n,n,steps,'random' if protocol == drones_team.PR_RANDOM else ('pseudo_random' if protocol == drones_team.PR_PSEUDO_RANDOM else 'deterministic')),"wb")
pickle.dump(statistics, f)
f.close()
