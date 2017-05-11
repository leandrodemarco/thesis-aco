#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import time
import networkx as nx
from Functions import buildGraph, cost, updatePheromone, isSolution
import Ant
import sys

def runAlgorithm(useCompleteModel, scenario1, isElitist, numElitists, \
                 nAnts, evapRate, tau_min, tau_max, costSigma, \
                 maxCycles, errScale, costFunction):

    start_time = time.time()

    errMax = 0.005 if scenario1 else 0.025
    useAllForUpdate = isElitist and numElitists == nAnts
    
    graph = buildGraph(useCompleteModel, scenario1, tau_min)
    nCycles = 0
    allSols = []
    
    while (nCycles < maxCycles):
        nCycles += 1
        pathsForCycle = []
    
        for i in range(0, nAnts):
            ant = Ant.Ant(graph, scenario1)
            path = ant.walkGraph()
            if (useAllForUpdate):
                pathsForCycle.append(path)

        updatePheromone(graph, tau_min, tau_max, evapRate, errMax, \
                        pathsForCycle, costSigma, errScale, costFunction)
        
        for path in pathsForCycle:
            if (isSolution(path, errMax) and not path in allSols):
                allSols.append(path)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print "\n\nAll sols: ", allSols, len(allSols)
    print "\nDuracion: ", elapsed_time 
    return (allSols, elapsed_time) 
