#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import time
import networkx as nx
from Functions import buildGraph, cost, updatePheromone, isSolution, \
                      buildSaturatedGraph, sensTotal
import Ant
import sys

def runExperiment(samples, scenario1, tau_min, tau_max):
    g, numPaths, numSols = buildSaturatedGraph(scenario1, tau_min, tau_max)
    errMax = 0.005 if scenario1 else 0.025
    results = []
    
    E = numPaths / numSols # Valor esperado para la binomial negativa
    print E
    
    for i in range(0, samples):
        print "Running experiment %i of %i" % (i+1, samples)
        antsUsed = 0
        success = False
        while (not success):
            ant = Ant.Ant(g, scenario1)
            path = ant.walkGraph()
            success = isSolution(path, errMax)
            antsUsed += 1
            
        results.append(antsUsed)
        #print results
        # Results deberia tener una distribucion negativa binomial
        # NB(p,r) con p=nroSols/totalCaminos y r=1 =>
        # E = r/p = totalCaminos / nroSols

    return results

def runAlgorithm(useCompleteModel, scenario1, nAnts, evapRate, tau_min, \
                tau_max, costSigma, maxCycles, errScale, costFunction, r1=None):

    start_time = time.time()

    errMax = 0.005 if scenario1 else 0.025
    
    graph, numPaths = buildGraph(useCompleteModel, scenario1, tau_min)
    nCycles = 0
    diffSols = []
    allSols = []
    
    minSens = 100.
    bestPath = None
    
    while (nCycles < maxCycles):
        nCycles += 1
        pathsForCycle = []
    
        for i in range(0, nAnts):
            ant = Ant.Ant(graph, scenario1, r1)
            path = ant.walkGraph()
            pathsForCycle.append(path)

        updatePheromone(graph, tau_min, tau_max, evapRate, errMax, \
                        pathsForCycle, costSigma, errScale, costFunction)
        
        for path in pathsForCycle:            
            if (isSolution(path, errMax)):
                pathSens = sensTotal(path)            
                if sensTotal(path) < minSens:
                    minSens = pathSens
                    bestPath = path                
                
                allSols.append(path)
                if (not path in diffSols):
                    diffSols.append(path)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print "\n\nAll sols: ", diffSols, len(diffSols)
    print "\nDuracion: ", elapsed_time 
    return (diffSols, elapsed_time, numPaths, len(allSols), minSens, bestPath) 
