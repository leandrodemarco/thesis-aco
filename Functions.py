#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import networkx as nx
import sys
import math

from filterSolutions import findSols

#isScenario1 = True
#errMax = 0.005 #if isScenario1 else 0.025

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

                     
def costLinear(omega, Q, targetOmega, targetQ, errMax):
    errOmega = abs((omega-targetOmega)/targetOmega)
    errQ = abs((Q-targetQ)/targetQ)
    
    resCost = 0
    if (errOmega > errMax):
        resCost += 1
    if (errQ > errMax):
        resCost += 1
        
    return resCost
    
    
def costExponential(term1, term2, scale):
    return (1. - math.exp(-(term1+term2)))/scale
    
def costPozo(omega, targetOmega, Q, targetQ, errMax, scale):
    x = (omega - targetOmega) / (2.*errMax*targetOmega)
    y = (Q - targetQ) / (2.*errMax*targetQ)
    
    resCost = 10**-6
    if (y >= -x and y <= x and x > 0.5):
        resCost = scale * x
    elif (x > -y and x < y and y > 0.5):
        resCost = scale * y
    elif (y >= x and y <= -x and x < -0.5):
        resCost = -scale * x
    elif (x > y and x < -y and y < -0.5):
        resCost = -scale * y
        
    return resCost
    
def costPozo45(omega, targetOmega, Q, targetQ):
    x = (omega - targetOmega) / targetOmega
    y = (Q - targetQ) / targetQ
    # Para dar mas (menos) pendiente a los lados multiplicar cada abs
    # por una k. Si k e {0,1} se le da menos pendiente

    k = 1.
    res = (k*abs(x) + k*abs(y) + 1) 

    return res
    
def costExp2(omega, targetOmega, Q, targetQ):
    x = (omega - targetOmega) / targetOmega
    y = (Q - targetQ) / targetQ
    
    cost = 1. / math.exp(-abs(x)) + 1. / math.exp(-abs(y)) - 1.
    return cost
    
def costL(omega, targetOmega, Q, targetQ, slope):
    # TODO: no hardcodear estos valores. calcularlos    
    xMax = 159.155
    xMin = 0.000179196
    yMax = 21.3198
    yMin = 0.0000479353
    
    x = omega / targetOmega
    y = Q / targetQ
    
    absmax = abs(xMax - 1) + abs(yMax - 1)
    cost = slope * (absmax - (abs(x-1.) + abs(y-1.)))

    return 1./cost

def costAcor(r1, r2, r3, c4, c5):
    res_min = 1000.
    res_max = 910000.
    cap_min = 1.0e-9
    cap_max = 8.2e-7
    g_wgt = 100000.
    light_wgt = 100.
    sens_wgt = 1000.
    obj_wp = 1000*2*math.pi
    obj_invq = math.sqrt(2.0)
    obj_g = 3.0
    
    r1_range_OK = r1 > res_min and r1 < res_max
    r2_range_OK = r2 > res_min and r2 < res_max
    r3_range_OK = r3 > res_min and r3 < res_max
    c4_range_OK = c4 > cap_min and c4 < cap_max
    c5_range_OK = c5 > cap_min and c5 < cap_max
    if all([r1_range_OK, r2_range_OK, r3_range_OK, c4_range_OK, 
           c5_range_OK]):
        a = r1/r2
        b = r1/r3
        sol_g = 1/a
        sol_sens = (2 + abs(1-a+b) + abs(1+a-b))/(2*(1+a+b))
        sol_w = math.sqrt(a*b/(c4*c5))/r1
        sol_invq = math.sqrt(c5/(c4*a*b))*(1+a+b)
        
        g_cost = g_wgt * (sol_g - obj_g) ** 2
        sens_cost = sens_wgt * sol_sens**2
        wp_cost = light_wgt * (math.log(sol_w/obj_wp))**2
        q_cost = light_wgt * (math.log(sol_invq/obj_invq))**2
        
        return sens_cost + g_cost + wp_cost + q_cost
    else:
        # Heavily penalize configurations that are not in the specified range
        return 1.0e11
                     
def cost(assignment, errMax, sigma, scale, costFunction=2):
    """
        @Params: costFunction: 1 => linear, 2 => exponential, 3 => pozo
                               4 => pozo 45º, 5 => exp2 , 6 => L-cost
    """
    r1 = assignment["r1"]
    r2 = assignment["r2"]
    r3 = assignment["r3"]
    c1 = assignment["c1"]
    c2 = assignment["c2"]
    
    omega = (1./(r2*r3*c1*c2))**(0.5)
    Q = qualityFactor(r1,r2,r3,c1,c2)
    
    targetOmega = 6283.9478 
    targetQ = 0.707
    
    term1 = ((omega - targetOmega)**2)/(2*sigma)
    term2 = ((Q - targetQ)**2)/(2*sigma)

    if (costFunction == 1):
        resCost = costLinear(omega, Q, targetOmega, targetQ, errMax)
    elif (costFunction == 2):
        resCost = costExponential(term1, term2, scale)
    elif (costFunction == 3):
        resCost = costPozo(omega, targetOmega, Q, targetQ, errMax, scale)
    elif (costFunction == 4):
        resCost = costPozo45(omega, targetOmega, Q, targetQ)
    elif (costFunction == 5):
        resCost = costExp2(omega, targetOmega, Q, targetQ)
    elif (costFunction == 6):
        resCost = costL(omega, targetOmega, Q, targetQ, 1.)
    elif (costFunction == 7):
        resCost = costAcor(r1, r2, r3, c1, c2)
        print resCost
    else:
        print "Error: Undefined cost Function"
        sys.exit()
        
    resCost += 0.001
    
    return resCost
    
def isSolution(assignment, errMax):
    r1 = assignment["r1"]
    r2 = assignment["r2"]
    r3 = assignment["r3"]
    c1 = assignment["c1"]
    c2 = assignment["c2"]
    
    errOmega = errorOmega(r2, r3, c1, c2, 6283.9478)
    errQ = errorQ(r1, r2, r3, c1, c2, 0.707)
    
    return errOmega < errMax and errQ < errMax
    
    
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
    
def sensTotal(path):
    """
        @params: Values for passive components of the circuit
        @returns: Sens_Total(components)
    """
    r1 = path["r1"]
    r2 = path["r2"]
    r3 = path["r3"]
    c1 = path["c1"]
    c2 = path["c2"]
    
    qFactor = qualityFactor(r1, r2, r3, c1, c2)
    s_r1, s_r2, s_r3 = sensitivities(qFactor, r1, r2, r3, c1, c2)
    
    print s_r1, s_r2, s_r3
    
    return abs(s_r1) + abs(s_r2) + abs(s_r3)
    
def _updatePher(assign, graph, minPher, maxPher, evaporationRate, \
                    errMax, costSigma, errScale, costFunction):
    
    #print "Updating pheromone"
    r1Node = ('r1', assign['r1'])
    r2Node = ('r2', assign['r2'])
    r3Node = ('r3', assign['r3'])
    c1Node = ('c1', assign['c1'])
    c2Node = ('c2', assign['c2'])
    
    edge1Pher = graph[r1Node][r2Node]['weight']
    edge2Pher = graph[r2Node][r3Node]['weight']
    edge3Pher = graph[r3Node][c1Node]['weight']
    edge4Pher = graph[c1Node][c2Node]['weight']

    assignCost = cost(assign, errMax, costSigma, errScale, \
                          costFunction)
    incPher = 1./assignCost
    
    pherInEdges = [edge1Pher, edge2Pher, edge3Pher, edge4Pher]
    index = 0
    for edgePherLvl in pherInEdges:
        edgePherLvl += incPher
        
        if (edgePherLvl < minPher):
            edgePherLvl = minPher
        elif (edgePherLvl > maxPher):
            edgePherLvl = maxPher
            
        pherInEdges[index] = edgePherLvl
        index += 1

    graph[r1Node][r2Node]['weight'] = pherInEdges[0]
    graph[r2Node][r3Node]['weight'] = pherInEdges[1]
    graph[r3Node][c1Node]['weight'] = pherInEdges[2]
    graph[c1Node][c2Node]['weight'] = pherInEdges[3]
    
def updatePheromone(graph, minPher, maxPher, evaporationRate, \
                    errMax, bestAssigns, costSigma, errScale, \
                    costFunction):
    """
        @params:
            *graph : the full graph
            *minPher & maxPher: minimum and maximum levels of pheromone
            *evaporationRate : self explaining
            *bestAssigns : a list containing best assignments of a given
               cycle.
    """
    useThreads = False
    
    if useThreads:
        manager = Manager()
        sharedGraph = manager.dict(graph) #WRONG! Can't "cast" like that
        jobs = []
        
        for assign in bestAssigns:
            j = multiprocessing.Process(target=_updatePher, \
                args=(assign, sharedGraph, minPher, maxPher, evaporationRate, \
                      errMax, costSigma, errScale, costFunction))
            jobs.append(j)
            
        for j in jobs:
            j.start()
            
        for j in jobs:
            j.join()
            
        graph = sharedGraph
        
        #~ pool = Pool()
        #~ 
        #~ partial_updatePher = partial(_updatePher, graph=graph, minPher=minPher, \
        #~ maxPher=maxPher, evaporationRate=evaporationRate, errMax=errMax, \
        #~ costSigma=costSigma, errScale=errScale, costFunction=costFunction)
        #~ 
        #~ pool.map_async(partial_updatePher, bestAssigns, len(bestAssigns)/cpu_count())
        #~ pool.close()
    else:
        for assign in bestAssigns:
            _updatePher(assign, graph, minPher, maxPher, evaporationRate, \
                         errMax, costSigma, errScale, costFunction)

def buildSaturatedGraph(isScenario1, minPher, maxPher):
    pathSols = findSols(isScenario1)
    g, numPaths = buildGraph(True, isScenario1, minPher)
    for sol in pathSols:
        r1Node = ('r1', sol['r1'])
        r2Node = ('r2', sol['r2'])
        r3Node = ('r3', sol['r3'])
        c1Node = ('c1', sol['c1'])
        c2Node = ('c2', sol['c2'])
        
        g[r1Node][r2Node]['weight'] = maxPher
        g[r2Node][r3Node]['weight'] = maxPher
        g[r3Node][c1Node]['weight'] = maxPher
        g[c1Node][c2Node]['weight'] = maxPher
        
    return g, numPaths, len(pathSols)
        
def buildGraph(useCompleteModel, isScenario1, minPher):
    if (useCompleteModel):
        return buildFullGraph(isScenario1, minPher)
    else:
        return buildReducedGraph(isScenario1, minPher)

def buildReducedGraph(isScenario1, minPher):
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
    
    errMax = 0.005 if isScenario1 else 0.025
    
    r1r2Edges = []
    for nR1 in r1Nodes:
        for nR2 in r2Nodes:
            if (errorG(nR1[1], nR2[1], 3) < errMax):
                r1r2Edges.append((nR1, nR2, minPher))
    
    #r1r2Edges = [(nR1,nR2,minPher) for nR1 in r1Nodes for nR2 in r2Nodes]
    r2r3Edges = [(nR2,nR3,minPher) for nR2 in r2Nodes for nR3 in r3Nodes]
    r3c1Edges = [(nR3,nC1,minPher) for nR3 in r3Nodes for nC1 in c1Nodes]
    c1c2Edges = [(nC1,nC2,minPher) for nC1 in c1Nodes for nC2 in c2Nodes]
    
    numPaths = len(r1r2Edges) * len(r3Nodes) * len(c1Nodes) * len(c2Nodes)
    
    g.add_weighted_edges_from(r1r2Edges)
    g.add_weighted_edges_from(r2r3Edges)
    g.add_weighted_edges_from(r3c1Edges)
    g.add_weighted_edges_from(c1c2Edges)
    
    return g, numPaths    
        
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
            res_val = res_base * (10**res_exp)
            res_values.append(round(res_val, 10))
            
    cap_values = []
    for cap_base in cap_bases:
        for cap_exp in cap_exps:
            cap_val = cap_base * (10**cap_exp)
            cap_values.append(round(cap_val, 10))     
    
    g = nx.Graph()
    r1Nodes = []
    r2Nodes = []
    r3Nodes = []
    c1Nodes = []
    c2Nodes = []
    
    for resVal in res_values:
        r1Nodes.append(("r1", resVal))
        r2Nodes.append(("r2", resVal))
        r3Nodes.append(("r3", resVal))
        
    for capVal in cap_values:
        c1Nodes.append(("c1", capVal))
        c2Nodes.append(("c2", capVal))
        
    errMax = 0.005 if isScenario1 else 0.025
        
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
    
    numPaths = len(r1r2Edges) * len(r3Nodes) * len(c1Nodes) * len(c2Nodes)
    
    g.add_weighted_edges_from(r1r2Edges)
    g.add_weighted_edges_from(r2r3Edges)
    g.add_weighted_edges_from(r3c1Edges)
    g.add_weighted_edges_from(c1c2Edges)
    
    #print len(g.nodes()), len(g.edges())    
        
    return g, numPaths
    
