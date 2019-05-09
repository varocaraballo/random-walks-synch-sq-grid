# -*- coding: utf-8 -*-
import random
from statistics_meters import ArcCoveringStatistics, DroneStatistics, TokenStatistics
import numpy as np

PR_RANDOM = 0
PR_PSEUDO_RANDOM = 1
PR_DETERMNISTIC = 2

def take_step_random_protocol(G, states, prev_states):
    k = len(states)
    for i in range(k):
        v = states[i]
        w = random.choice(G[v])
        prev_states[i] = v
        states[i] = w
        
def take_step_pseudo_random_protocol(G, states, prev_states):
    k = len(states)
    occupied_vertices= {}
    for i in range(k):
        v = states[i]
        occupied_vertices.setdefault(v,[])
        occupied_vertices[v].append(i)
    for v in occupied_vertices:
        drones = occupied_vertices[v]
        if len(drones)>1:
            assert len(drones) == 2
            if prev_states[drones[0]] is None and prev_states[drones[1]] is None:
                states[drones[1]] = G[v][1]
                states[drones[0]] = G[v][0]
            else:                    
                states[drones[1]] = tuple(2*np.array(v)-np.array(prev_states[drones[0]]))                            
                states[drones[0]] = tuple(2*np.array(v)-np.array(prev_states[drones[1]]))
            prev_states[drones[0]] = prev_states[drones[1]] = v
        else:
            states[drones[0]] = random.choice(G[v])
            prev_states[drones[0]] = v

def take_step_deterministic_protocol(G, states, prev_states):
    k = len(states)
    occupied_vertices= {}
    for i in range(k):
        v = states[i]
        occupied_vertices.setdefault(v,[])
        occupied_vertices[v].append(i)
    for v in occupied_vertices:
        drones = occupied_vertices[v]
        if len(drones)>1:
            assert len(drones) == 2
            if prev_states[drones[0]] is None and prev_states[drones[1]] is None:
                states[drones[1]] = G[v][1]
                states[drones[0]] = G[v][0]
            else:                    
                states[drones[1]] = tuple(2*np.array(v)-np.array(prev_states[drones[0]]))                            
                states[drones[0]] = tuple(2*np.array(v)-np.array(prev_states[drones[1]]))
            prev_states[drones[0]] = prev_states[drones[1]] = v
        else:
            if prev_states[drones[0]] is None:
                states[drones[0]] = random.choice(G[v])
            else:                
                w = tuple(2*np.array(v)-np.array(prev_states[drones[0]]))
                states[drones[0]] = w if w in G[v] else G[v][0]
            prev_states[drones[0]] = v

take_step = [take_step_random_protocol, take_step_pseudo_random_protocol, take_step_deterministic_protocol]
            
def simula(G, startingPositions, k, steps, protocol, arcsToStudy=None):
    arcsCoveringStatistics = {}
    for v in G:
        for w in G[v]:            
            arcsCoveringStatistics[(v,w)] = ArcCoveringStatistics(keepData = True if arcsToStudy is not None and (v,w) in arcsToStudy else False)
            
    dronesStatistics = [DroneStatistics() for i in range(k)]  
    states_indexes = np.random.choice([i for i in range(len(startingPositions))], size=k, replace = protocol == PR_RANDOM)
    states = [startingPositions[i] for i in states_indexes]
    prev_states = [None]*k
    
    take_step[protocol](G, states, prev_states)
    
    occupied_vertices = {}
    for i in range(k):
        state = states[i]
        occupied_vertices.setdefault(state, set()).add(i)
        
    for group in occupied_vertices.values():
        if len(group)>1:
            for r in group:
                dronesStatistics[r].meeting(0, group.difference({r}))
    
    for j in range(steps):        
        occupied_vertices.clear()        
        take_step[protocol](G, states, prev_states)
        for i in range(k):
            state = states[i]
            prev_state = prev_states[i]
            occupied_vertices.setdefault(state, set()).add(i)
            arcsCoveringStatistics[(prev_state,state)].visit(j)
        for group in occupied_vertices.values():
            if len(group)>1:
                for r in group:
                    dronesStatistics[r].meeting(j+1, group.difference({r}))        
    
    s = 0
    c = 0
    arcs_idle_data = {}
    for arc in arcsCoveringStatistics:
        st = arcsCoveringStatistics[arc]        
        arc_avg_idle = st.avg_idle if st.avg_idle != float('inf') else steps        
        arcs_idle_data[arc] = arc_avg_idle        
        s += arc_avg_idle
        c += 1
    avg_idle = s/c       
    s = 0
    c = 0
    min_isolation = float('inf')
    max_isolation = -1   
    for st in dronesStatistics:
        drone_avg_isolation = st.avg_isolation if st.avg_isolation != float('inf') else steps
        min_isolation = min(min_isolation, drone_avg_isolation)
        max_isolation = max(max_isolation, drone_avg_isolation)
        s += drone_avg_isolation
        c += 1
    avg_isolation = s/c
    assert c == k
    
    return (avg_idle, arcs_idle_data, min_isolation, avg_isolation, max_isolation),\
            {arc:arcsCoveringStatistics[arc].data for arc in arcsToStudy} if arcsToStudy is not None else None


def broadcast_time(G, startingPositions, k, protocol, max_iter, checkConnectivity):
    creator = random.randint(0,k-1)
    token = TokenStatistics(0, creator, k, {creator})   
    
    states_indexes = np.random.choice([i for i in range(len(startingPositions))], size=k, replace = protocol == PR_RANDOM)
    states = [startingPositions[i] for i in states_indexes]
    prev_states = [None]*k    
    take_step[protocol](G, states, prev_states)
    
    if checkConnectivity is not None and protocol == PR_DETERMNISTIC:
        if not checkConnectivity(states, prev_states):
            return float('inf')
    
    occupied_vertices = {}
    for i in range(k):
        state = states[i]
        occupied_vertices.setdefault(state, set()).add(i)
        
    for group in occupied_vertices.values():
        t = token.isBroadCasted(k, 0, group)
        if t is not None:
            return t
    
    i = 1
    while True and i<=max_iter:
        occupied_vertices.clear()
        take_step[protocol](G, states, prev_states)
        for j in range(k):
            state = states[j]
            occupied_vertices.setdefault(state, set()).add(j)                       
        for group in occupied_vertices.values():
            t = token.isBroadCasted(k, i, group)
            if t is not None:
                return t
        i += 1
    return float('inf')
            
                