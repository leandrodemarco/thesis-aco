#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import networkx as nx
import sys
from math import exp

isScenario1 = False
errMax = 0.005 if isScenario1 else 0.025

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

def cost(assignment, errMax):
    if (len(assignment) == 0):
        return float('inf')
    #print assignment
    r1 = assignment["r1"]
    r2 = assignment["r2"]
    r3 = assignment["r3"]
    c1 = assignment["c1"]
    c2 = assignment["c2"]
    
    omega = (1./(r2*r3*c1*c2))**(0.5)
    Q = qualityFactor(r1,r2,r3,c1,c2)
    
    targetOmega = 6283.9478 
    targetQ = 0.707
    
    sigma = errMax
    term1 = ((omega - targetOmega)**2)/(2*sigma)
    term2 = ((Q - targetQ)**2)/(2*sigma)

    print assignment, omega, Q
    raw_input()
    
    return 1. - exp(-(term1+term2))
    
def errorG(r1, r2, Gf):
    Gy = r2/r1
    return abs((Gy-Gf)/Gf)
    
def errorOmega(r2, r3, c1, c2, omegaF):
    omegaY = (1./(r2*r3*c1*c2))**(0.5)
    return abs((omegaY-omegaF)/omegaF)
    
def errorQ(r1,r2,r3,c1,c2, Qf):
    Qy = qualityFactor(r1,r2,r3,c1,c2)
    return abs((Qy-Qf)/Qf)
    
def qualityFactor(r1,r2,r3,c1,c2):
    fact_1 = (c2/c1)**(0.5)

    term_1 = ((r2*r3)**(0.5))/r1
    term_2 = (r3/r2)**(0.5)
    term_3 = (r2/r3)**(0.5)

    fact_2 = term_1 + term_2 + term_3
    return 1./(fact_1 * fact_2)
    
def sensitivities(qFactor, r1, r2, r3, c1, c2):
    """
        @params: quality factor (Qp) and component values
        @returns: sensitivity of r1, r2 and r3 relative to Qp
        @observation: we compute all sensitivities together to avoid
        computing square roots unnecessarily
    """
    fact_1 = -qFactor/2.0
    
    term_1 = (1.0/r1)*(((r2*r3*c2)/c1)**(0.5))
    term_2 = ((r3*c2)/(r2*c1))**(0.5)
    term_3 = ((r2*c2)/(r3*c1))**(0.5)
    
    fact_2 = term_1 - term_2 + term_3
    sens_r2 = fact_1*fact_2
    
    fact_2 = term_1 + term_2 - term_3
    sens_r3 = fact_1 * fact_2
    
    sens_r1 = qFactor*term_1
    
    return sens_r1, sens_r2, sens_r3
    
def sensTotal(r1, r2, r3, c1, c2):
    """
        @params: Values for passive components of the circuit
        @returns: Sens_Total(components)
    """
    qFactor = qualityFactor(r1, r2, r3, c1, c2)
    s_r1, s_r2, s_r3 = sensitivities(qFactor, r1, r2, r3, c1, c2)
    
    return (1./3.)*(abs(s_r1) + abs(s_r2) + abs(s_r3))

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
            if (nodeInAssign(n1, assign) and nodeInAssign(n2, assign)):
                incPher += 1./(cost(assign, errMax)+0.001)
        
        newPher = (1.-evaporationRate)*pherLvl + incPher
        if (newPher < minPher):
            newPher = minPher
        elif (newPher > maxPher):
            newPher = maxPher
        
        graph[n1][n2]['weight'] = newPher
        
def nodeInAssign(node, assignment):
    compName = node[0]
    compVal = node[1]
    return compName in assignment.keys() and assignment[compName] == compVal

def buildGraph(useCompleteModel, isScenario1, minPher):
    if (useCompleteModel):
        return buildFullGraph(isScenario1, minPher)
    else:
        return buildReducedGraph(minPher)

def buildReducedGraph(minPher):
    r1_values = [1600., 2700., 3000., 3300., 3600., 5100.]
    r2_values = [4700., 8200., 9100., 10000., 11000., 15000.]
    r3_values = [1300., 1500., 1600., 1800., 2000., 2200., 2400., 2700., 3000.]
    c1_values = [6.8e-8, 8.2e-8, 1.0e-7, 1.2e-7, 1.5e-7, 1.8e-7]
    c2_values = [8.2e-9, 1.0e-8, 1.2e-8, 1.5e-8, 1.8e-8, 2.2e-8]

    g = nx.Graph()
    r1Nodes = [("r1", val) for val in r1_values]
    r2Nodes = [("r2", val) for val in r2_values]
    r3Nodes = [("r3", val) for val in r3_values]
    c1Nodes = [("c1", val) for val in c1_values]
    c2Nodes = [("c2", val) for val in c2_values]
    
    r1r2Edges = [(nR1,nR2,minPher) for nR1 in r1Nodes for nR2 in r2Nodes]
    r2r3Edges = [(nR2,nR3,minPher) for nR2 in r2Nodes for nR3 in r3Nodes]
    r3c1Edges = [(nR3,nC1,minPher) for nR3 in r3Nodes for nC1 in c1Nodes]
    c1c2Edges = [(nC1,nC2,minPher) for nC1 in c1Nodes for nC2 in c2Nodes]
    
    g.add_weighted_edges_from(r1r2Edges)
    g.add_weighted_edges_from(r2r3Edges)
    g.add_weighted_edges_from(r3c1Edges)
    g.add_weighted_edges_from(c1c2Edges)
    
    lNodes = r1Nodes+r2Nodes+r3Nodes+c1Nodes+c2Nodes
    adj_matrix = nx.adjacency_matrix(g)
    #print nx.to_dict_of_dicts(g)[('r3', 1300.0)]
    #print adj_matrix(lNodes)
    
    return g    
        
def buildFullGraph(isScenario1, minPher):
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
        
    r1r2Edges = []
    validR2Nodes = []
    for nR1 in r1Nodes:
        for nR2 in r2Nodes:
            if (errorG(nR1[1], nR2[1], 3) < errMax):
                r1r2Edges.append((nR1, nR2, minPher))
                validR2Nodes.append(nR2)      
    
    r2r3Edges = [(nR2,nR3,minPher) for nR2 in validR2Nodes for nR3 in r3Nodes]    
    r3c1Edges = [(nR3,nC1,minPher) for nR3 in r3Nodes for nC1 in c1Nodes]
    c1c2Edges = [(nC1,nC2,minPher) for nC1 in c1Nodes for nC2 in c2Nodes]
    
    g.add_weighted_edges_from(r1r2Edges)
    g.add_weighted_edges_from(r2r3Edges)
    g.add_weighted_edges_from(r3c1Edges)
    g.add_weighted_edges_from(c1c2Edges)    
        
    return g
    
