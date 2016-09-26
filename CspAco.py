#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import time
import networkx as nx
from Functions import buildGraph, cost, updatePheromone
import Ant
import sys

start_time = time.time()

isScenario1 = False
minPher = 0.3
maxPher = 3.
evaporationRate = 0.2

graph = buildGraph(isScenario1, minPher)
#print graph.edges(data=True)[0]
#sys.exit()
bestAssignment = {}
maxCycles = 10
nAnts = 3000
nCycles = 0
errMax = 0.005 if isScenario1 else 0.025

while (cost(bestAssignment, errMax) > 0 or nCycles < maxCycles):
    print nCycles
    nCycles += 1 
    for i in range(0, nAnts):
        ant = Ant.Ant(graph, isScenario1)
        assignment = ant.walkGraph()
        if (cost(assignment, errMax) == 0):
            print assignment
            bestAssignment = assignment
        #if (cost(assignment, errMax) < cost(bestAssignment, errMax)):
            #bestAssignment = assignment
    updatePheromone(graph, minPher, maxPher, evaporationRate, [bestAssignment])
