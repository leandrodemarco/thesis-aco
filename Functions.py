#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import networkx as nx

e12_values = [1., 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
    
e24_values = [1., 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2, 2.2, 2.4, 2.7, 3, \
              3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, \
              9.1]
              
e96_values = [1., 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24,\
              1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, \
              1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, \
              1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, \
              2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, \
              3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, \
              3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, \
              4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, \
              5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, \
              7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, \
              8.87, 9.09, 9.31, 9.53, 9.76]

def cost(assignment):
    if (len(assignment) == 0):
        return float("inf")
    
    return 0.

def updatePheromone(graph, minPher, maxPher, evaporationRate, bestAssigns):
    """
        @params:
            *graph : the full graph
            *minPher & maxPher: minimum and maximum levels of pheromone
            *evaporationRate : self explaining
            *bestAssigns : a list containing best assignments of a given
               cycle. The amount of assignments here differs whether
               using an all-ants, elitist-ants or single-ant approach
    """
    for edge in graph.edges(data=True):
        n1, n2, pherDict = edge
        pherLvl = pherDict['weight']
        #n1 = (c1, val1) and n2 = (c2, val2) ~ (filterComp, val)
            
        incPher = .0
        for assign in bestAssigns:
            if (n1 in assign and n2 in assign):
                incPher += 1./cost(assign)
        
        newPher = (1.-evaporationRate)*pherLvl + incPher
        if (newPher < minPher):
            newPher = minPher
        elif (newPher > maxPher):
            newPher = maxPher
        
        graph[n1][n2]['weight'] = newPher

def buildGraph(isScenario1, minPher):
    res_bases = e24_values
    if (isScenario1): res_bases = e96_values

    cap_bases = e12_values
    if (isScenario1): cap_bases = e24_values

    res_exps = [3,4,5]
    cap_exps = [-7,-8,-9]

    res_values = []
    for res_base in res_bases:
        for res_exp in res_exps:
            res_values.append(res_base * (10**res_exp))
            
    cap_values = []
    for cap_base in cap_bases:
        for cap_exp in cap_exps:
            cap_val = cap_base * (10**cap_exp)
            cap_values.append(cap_base * (10**cap_exp))
    
    varNames = ["r1", "r2", "r3", "c1", "c2"]       
    
    g = nx.Graph()
    r1Nodes = []
    r2Nodes = []
    r3Nodes = []
    r4Nodes = []
    c1Nodes = []
    c2Nodes = []
    
    for resVal in res_values:
        r1Nodes.append(("r1", resVal))
        r2Nodes.append(("r2", resVal))
        r3Nodes.append(("r3", resVal))
        
    for capVal in cap_values:
        c1Nodes.append(("c1", capVal))
        c2Nodes.append(("c2", capVal))
        
    r1r2Edges = [(nR1,nR2,minPher) for nR1 in r1Nodes for nR2 in r2Nodes]
    #r1r3Edges = [(nR1,nR3,minPher) for nR1 in r1Nodes for nR3 in r3Nodes]
    #r1c1Edges = [(nR1,nC1,minPher) for nR1 in r1Nodes for nC1 in c1Nodes]
    #r1c2Edges = [(nR1,nC2,minPher) for nR1 in r1Nodes for nC2 in c2Nodes]
    
    r2r3Edges = [(nR2,nR3,minPher) for nR2 in r2Nodes for nR3 in r3Nodes]
    r2c1Edges = [(nR2,nC1,minPher) for nR2 in r2Nodes for nC1 in c1Nodes]
    r2c2Edges = [(nR2,nC2,minPher) for nR2 in r2Nodes for nC2 in c2Nodes]
    
    r3c1Edges = [(nR3,nC1,minPher) for nR3 in r3Nodes for nC1 in c1Nodes]
    r3c2Edges = [(nR3,nC2,minPher) for nR3 in r3Nodes for nC2 in c2Nodes]
    
    c1c2Edges = [(nC1,nC2,minPher) for nC1 in c1Nodes for nC2 in c2Nodes]
    
    g.add_weighted_edges_from(r1r2Edges)
    #g.add_weighted_edges_from(r1r3Edges)
    #g.add_weighted_edges_from(r1c1Edges)
    #g.add_weighted_edges_from(r1c2Edges)
    g.add_weighted_edges_from(r2r3Edges)
    g.add_weighted_edges_from(r2c1Edges)
    g.add_weighted_edges_from(r2c2Edges)
    g.add_weighted_edges_from(r3c1Edges)
    g.add_weighted_edges_from(r3c2Edges)    
    g.add_weighted_edges_from(c1c2Edges)    
        
    return g
    
