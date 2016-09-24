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
bestAssignment = []
maxCycles = 100
nAnts = 10
nCycles = 0

while (cost(bestAssignment) > 0 or nCycles < maxCycles):
    nCycles += 1 
    for i in range(0, nAnts):
        ant = Ant.Ant(graph, isScenario1)
        assignment = ant.walkGraph()
        if (cost(assignment) < cost(bestAssignment)):
            bestAssignment = assignment
	updatePheromone(graph, minPher, maxPher, evaporationRate, [bestAssignment])

print bestAssignment

