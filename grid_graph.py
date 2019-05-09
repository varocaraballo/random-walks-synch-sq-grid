# -*- coding: utf-8 -*-
import numpy as np
import fractions as frac


# It is assumed that circles in coordinates (row=r, col=c) is clockwise if (r+c)%2 == 1, counterclockwise otherwise.

def displacementToAdjacents(circle_row, circle_col):
    """
    Returns the displacements (dr, dc) such that (circle_row+dr, circle_col+dc) is reachable from (circle_row, circle_col)
    """
    r = 1 if circle_row%2==0 else 2
    c = 2 if circle_col%2==0 else 1
    l = [(0,0)]*16
    for i in range(4):
        for j in range(4):
            l[i*4+j] = (i-r, j-c)
    return l


def diamondGridGraph(n, m):
    dr = np.array([1, 1, -1, -1])
    dc = np.array([-1, 1, 1, -1])
    _dc = -1*dc
    G = {}
    for i in range(n):
        for j in range(m):
            s = (i*2,j*2+1)            
            d = dc if (i+j)%2 == 0 else _dc
            for l in range(4):
                G.setdefault(s,[])
                ns = tuple(np.array(s)+np.array([dr[l], d[l]]))
                G[s].append(ns)                                                
                s = ns
    return G
            
            
def getStartVertexInDiamondGridGraph(circle_row, circle_col):
    return (circle_row*2+1, circle_col*2 + (0  if circle_col % 2 == 0 else 2)) 

def getEndArcInDiamondGridGraph(circle_row, circle_col):
    center = (circle_row*2+1, circle_col*2+1)
    return (tuple(np.array(center)+np.array([-1, 0] if circle_row%2 == 0 else [1, 0])),
            tuple(np.array(center)+np.array([0, -1] if circle_col%2 == 0 else [0, 1])))
        

def transitionProbability(G, startVertex, endArc):
    from collections import deque
    visiteds = {startVertex}
    q = deque()
    q.append((startVertex, frac.Fraction(1)))
    while len(q)>0:
        v,p = q.popleft()
        neighbors = G[v]
        np = p/len(neighbors)
        for w in neighbors:
            if w == endArc[1] and v == endArc[0]:
                return np
            if w not in visiteds:
                q.append((w, np))        
                visiteds.add(w)
    
    
def getGridTransitionMatrix(n,m):
    t = n*m
    M = np.zeros((t,t), dtype=frac.Fraction)
    dgg = diamondGridGraph(n,m)
    for i in range(t):
        r = int(i/m)
        c = i%m
        l = displacementToAdjacents(r,c)
        for dr,dc in l:
            if 0<=r+dr<n and 0<=c+dc<m:                
                M[i, (r+dr)*m+c+dc] = transitionProbability(dgg, 
                 getStartVertexInDiamondGridGraph(r,c), 
                 getEndArcInDiamondGridGraph(r+dr, c+dc))
    return M


def gridMixingTime(n,m, e = frac.Fraction(1,4)):
    e = e**2
    M = getGridTransitionMatrix(n,m)
    t = n*m
    I = np.identity(t, dtype=float)    
    error = float('inf')
    c = 0
    stationary = frac.Fraction(1,t)*np.ones(t, dtype=frac.Fraction)
    while error>=e:
        c += 1
        I = np.dot(I,M)
        error = -1
        for i in range(t):
            dif = np.matrix(I[i]-stationary)
            error = max(error, np.dot(dif,np.transpose(dif)))        
    return c

def grid2PoweredMixingTime(n,m, e = frac.Fraction(1,4)):
    e = e**2
    M = getGridTransitionMatrix(n,m)
    t = n*m
    error = -1
    c = 1
    stationary = frac.Fraction(1,t)*np.ones(t, dtype=frac.Fraction)
    for i in range(t):
            dif = np.matrix(M[i]-stationary)
            error = max(error, np.dot(dif,np.transpose(dif)))       
    while error>=e:
        c *= 2
        M = np.dot(M,M)
        error = -1
        for i in range(t):
            dif = np.matrix(M[i]-stationary)
            error = max(error, np.dot(dif,np.transpose(dif)))        
    return c
        

            