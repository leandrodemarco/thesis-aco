#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import time
import networkx as nx
from Functions import buildGraph, cost, updatePheromone, isScenario1, errMax
import Ant
import sys

start_time = time.time()

minPher = 1.0
maxPher = 6.0
evaporationRate = 0.05

graph = buildGraph(isScenario1, minPher)
#print graph.edges(data=True)[0]
#sys.exit()
bestAssignment = {}
maxCycles = 1000
nAnts = 15
nCycles = 0

while (cost(bestAssignment, errMax) > 0 and nCycles < maxCycles):
    nCycles += 1 
    for i in range(0, nAnts):
        #print nCycles, i
        ant = Ant.Ant(graph, isScenario1)
        assignment = ant.walkGraph()
        #print assignment
        if (cost(assignment, errMax) < cost(bestAssignment, errMax)):
            bestAssignment = assignment
    #print "Updating pheromone", cost(assignment, errMax), cost(bestAssignment, errMax)
    updatePheromone(graph, minPher, maxPher, evaporationRate, [bestAssignment])

print bestAssignment, cost(bestAssignment, errMax)
