#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import time
import networkx as nx
from Functions import buildGraph, cost, updatePheromone, isSolution
import Ant
import sys
import threading
import multiprocessing

class AntThread(threading.Thread):
    def __init__(self, graph, scenario1, pathList):
        threading.Thread.__init__(self)
        self.graph = graph
        self.scenario1 = scenario1
        self.pathList = pathList
        
    def run(self):
        ant = Ant.Ant(self.graph, self.scenario1)
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
    
        if (useThreads):
            nrOfCores = multiprocessing.cpu_count()
            # Launch up to 2*nrOfCores thread to prevent overhead
            nrOfThreads = nrOfCores
            antsRemaining = nAnts # Ants that still need to run
            while (antsRemaining > 0):
                blockThreads = [] # Threads that will be launched in this iteration
                threadsNeeded = min(nrOfThreads, antsRemaining)
                for i in range(0, threadsNeeded):
                    newThread = AntThread(graph, scenario1, pathsForCycle)
                    blockThreads.append(newThread)
                    newThread.start()
                    
                for t in blockThreads:
                    # Wait for all threads in this block to finish
                    t.join()
                    
                antsRemaining -= threadsNeeded
        else:
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
