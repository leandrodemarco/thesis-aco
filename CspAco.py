#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import time
import networkx as nx
from Functions import buildGraph, cost, updatePheromone, isScenario1, errMax
import Ant
import sys

def runAlgorithm(useCompleteModel, scenario1, isElitist, numElitists, \
nAnts, evapRate, tau_min, tau_max, costSigma, maxCycles):

    start_time = time.time()

    graph = buildGraph(useCompleteModel, scenario1, tau_min)
        
bestAssignment = {}
maxCycles = 1000
nAnts = 15
nCycles = 0

#~ while (cost(bestAssignment, errMax) > 0 and nCycles < maxCycles):
    #~ nCycles += 1 
    #~ for i in range(0, nAnts):
        #~ #print nCycles, i
        #~ ant = Ant.Ant(graph, isScenario1)
        #~ assignment = ant.walkGraph()
        #~ #print assignment
        #~ if (cost(assignment, errMax) < cost(bestAssignment, errMax)):
            #~ bestAssignment = assignment
    #~ #print "Updating pheromone", cost(assignment, errMax), cost(bestAssignment, errMax)
    #~ updatePheromone(graph, minPher, maxPher, evaporationRate, [bestAssignment])
#~ 
#~ print bestAssignment, cost(bestAssignment, errMax)
