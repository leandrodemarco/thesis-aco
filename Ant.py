#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from Functions import e12_values, e24_values, e96_values, cost
import numpy as np
from random import sample
import sys

class Ant:
    def __init__(self, graph, isScenario1):
        # Public attributes
        self.path = {} # path[compName] = compVal
        self.position = None # Node (comp, compVal) where ant is standing
        self.varNames = ["r1", "r2", "r3", "c1", "c2"]
        self.graph = graph
        self.assignedVars = []
        self.pherFactor = 1.0
        self.heurFactor = 1. - self.pherFactor
        self.isScenario1 = isScenario1
        
    def chooseNextNode(self):
        #UPDATE POSITION HERE!!!
        if self.position == None:
            # Start with a R1 node as it reduces R2 choices. How do we
            # rank R1-nodes? 
            # Prob(r1, val) = sum(pherOnEdgesLeavingNode)/totalPherLeavingR1Edges
            totalPheromone = .0
            
            nodeProb = {}
            
            r1Nodes = [node for node in self.graph.nodes() if node[0] == "r1"]
            for r1Node in r1Nodes:
                edgesLeavingNode = self.graph.edges([r1Node])
                pherForNode = 0.
                for edge in edgesLeavingNode:
                    n0, n1 = edge
                    pherOnEdge = self.graph[n0][n1]['weight']
                    pherForNode += pherOnEdge
                    totalPheromone += pherOnEdge
                    
                nodeProb[r1Node] = pherForNode
                
            for r1Node, probNode in nodeProb.items():
                nodeProb[r1Node] /= totalPheromone
            
            lVals = []
            for r1Node in nodeProb.keys():
                lVals.append(r1Node[1])
            
            selectedVal = np.random.choice(lVals, 1, nodeProb.values())[0]
            self.position = ("r1", selectedVal)
                 
        #currentVar = self.position[0]
        elif self.position[0] == "r1":            
            newNode = self.chooseValForVar("r2")
            self.position = newNode
        elif self.position[0] == "r2":
            newNode = self.chooseValForVar("r3")
            self.position = newNode
        elif self.position[0] == "r3":
            newNode = self.chooseValForVar("c1")
            self.position = newNode
        elif self.position[0] == "c1":
            newNode = self.chooseValForVar("c2")
            self.position = newNode
            
        self.path[self.position[0]] = self.position[1]
        
    def chooseValForVar(self, var):
        """ 
            Selects value for variable var probabilistically based on 
            pheromone on edge
        """
        edgesLeavingNode = self.graph.edges(self.position)
        possibleValues = []
        for e in edgesLeavingNode:
            targetNode = e[1]
            if (targetNode[0] == var):
                possibleValues.append(targetNode[1])

        probBaseDict = {}
        sumOfProbs = 0.
        for possibleVal in possibleValues:
            theNode = (var, possibleVal)
            pherOnEdge = self.graph[self.position][theNode]['weight']
            pherParam = pherOnEdge**self.pherFactor
            
            errMax = 0.005 if self.isScenario1 else 0.025
            
            #~ tmpPath = self.path.copy()
            #~ tmpPath[theNode[0]] = theNode[1]
            #~ heurForEdge = 1./(1. + cost(tmpPath, errMax) - cost(self.path, errMax))
            #~ heurParam = heurForEdge**self.heurFactor
            
            probBaseDict[theNode] = pherParam #* heurParam
            sumOfProbs += pherParam #* heurParam
        
        for node, prob in probBaseDict.items():
            probBaseDict[node] = probBaseDict[node]/sumOfProbs
        
        lVals = []
        for node in probBaseDict.keys():
            lVals.append(node[1])
        
        selectedVal = np.random.choice(lVals, 1, probBaseDict.values())[0]
        nodeArr = (var, selectedVal)
        return nodeArr


    def walkGraph(self):
        while (set(self.assignedVars) != set(self.varNames)):
            self.chooseNextNode()
            newAssignedVar = self.position[0]
            self.assignedVars.append(newAssignedVar)

        return self.path
