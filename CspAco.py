#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import time
import networkx as nx
from Functions import buildGraph, cost, updatePheromone, isSolution
import Ant
import sys
import threading

class AntThread(threading.Thread):
    def __init__(self, graph, scenario1, pathList):
        threading.Thread.__init__(self)
        #self.AntPath = []
        self.graph = graph
        self.scenario1 = scenario1
        self.pathList = pathList
        
    def run(self):
        ant = Ant.Ant(self.graph, self.scenario1)
        #self.AntPath = ant.walkGraph()
        self.pathList.append(ant.walkGraph())

def runAlgorithm(useCompleteModel, scenario1, isElitist, numElitists, \
                 nAnts, evapRate, tau_min, tau_max, costSigma, \
                 maxCycles, errScale, costFunction):

    start_time = time.time()

    errMax = 0.005 if scenario1 else 0.025
    useAllForUpdate = isElitist and numElitists == nAnts
    
    graph = buildGraph(useCompleteModel, scenario1, tau_min)
    nCycles = 0
    allSols = []
    
    useThreads = False
    
    while (nCycles < maxCycles):
        nCycles += 1
        pathsForCycle = []
        
        allThreads = []
        for i in range(0, nAnts):
                if (useThreads):
                    newThread = AntThread(graph, scenario1, pathsForCycle)
                    allThreads.append(newThread)
                    newThread.start()
                else:
                    ant = Ant.Ant(graph, scenario1)
                    path = ant.walkGraph()
                    if (useAllForUpdate):
                        pathsForCycle.append(path)
        
        if (useThreads):        
            for t in allThreads:
                t.join()
            print "Terminaron todos los threads"
        
        print len(pathsForCycle)
        updatePheromone(graph, tau_min, tau_max, evapRate, errMax, \
                        pathsForCycle, costSigma, errScale, costFunction)
        
        for path in pathsForCycle:
            if (isSolution(path, errMax)):
                allSols.append(path)
                #print path
    
    end_time = time.time()
    elapsed_time = end_time - start_time            
    print "\n\nAll sols: ", allSols, len(allSols)
    print "\nDuracion: ", elapsed_time 
