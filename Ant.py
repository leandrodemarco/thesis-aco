#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from Functions import e12_values, e24_values, e96_values, cost
import numpy as np
from random import sample

class Ant:
    def __init__(self, graph, isScenario1):
        # Public attributes
        self.path = {} # path[compName] = compVal
        self.position = None # Node (comp, compVal) where ant is standing
        self.varNames = ["r1", "r2", "r3", "c1", "c2"]
        self.graph = graph
        self.assignedVars = []
        self.pherFactor = 0.8
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
            possibleValues = e96_values if self.isScenario1 else e24_values
            for posVal in possibleValues:
                for resExp in [3,4,5]:
                    r1Node = ("r1", posVal * (10**resExp))
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
                  
        elif self.position[0] == "r1":
            newNode = self.chooseValForVar("r2")
            self.position = newNode                            
        else:
            """
                All nodes of var xj are connected to every other node of xi!=xj
                We are using cascaded decision where we first choose an
                unassigned variable and then a value for that var.
                We are using dynamic-random variable ordering so just choose
                randomly from unassigned vars
            """
            unassignedVars = set(self.varNames).difference(set(self.assignedVars))
            nextVar = np.random.choice(list(unassignedVars), 1)[0]
            # We need to pick a value for this chosen var
            newNode = self.chooseValForVar(nextVar)
            self.position = newNode
            
        self.path[self.position[0]] = self.position[1]
        
    def chooseValForVar(self, var):
        """ 
            Selects value for variable var probabilistically based on 
            pheromone on ed
        """
        varIsResistor = var.startswith("r")
        if (varIsResistor):
            possibleValues = e96_values if self.isScenario1 else e24_values
        else:
            possibleValues = e24_values if self.isScenario1 else e12_values
            
        exponents = [3,4,5] if varIsResistor else [-7,-8,-9] 
            
        probBaseDict = {}
        sumOfProbs = 0.
        for possibleVal in possibleValues:
            for exp in exponents:
                theNode = (var, possibleVal * (10**exp))
                #print self.position, theNode
                pherOnEdge = self.graph[self.position][theNode]['weight']
                pherParam = pherOnEdge**self.pherFactor
                
                errMax = 0.005 if self.isScenario1 else 0.025
                
                tmpPath = self.path.copy()
                tmpPath[theNode[0]] = theNode[1]
                heurForEdge = 1./(1. + cost(tmpPath, errMax) - cost(self.path, errMax))
                heurParam = heurForEdge**self.heurFactor
                
                probBaseDict[theNode] = pherParam * heurParam
                sumOfProbs += pherParam * heurParam
        
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
