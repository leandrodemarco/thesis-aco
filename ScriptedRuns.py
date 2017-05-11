#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from CspAco import runAlgorithm

runsPerExperiment = 25

completeModel = True
scenario1 = True
isElitist = True
#~ antsPerCycle = [(100, 10), (1000, 10), (10000, 10), (1000, 1000)]
#~ evapRateVals = [0.05, 0.20, 0.25]
#~ tauMinVals = [0.15 ,0.20 0.35, 0.50]
#~ tauMaxVals = [40, 60, 80, 100]
#~ sigmaVals = [0.05, 0.10, 0.15]
#~ errScaleVals = [4,5,6]
costFunctionVals = [1,2,3]

#~ totalCases = len(antsPerCycle) * len(evapRateVals) * len(tauMinVals) \
                  #~ * len(tauMaxVals) * len(sigmaVals) * len(errScaleVals) \
                  #~ * len(costFunctionVals)

f = open('ScriptedResults.txt', 'w')

numCase = 1
solsPerCostFun = {1: [], 2: [], 3: []}
uniqueSolsPerCostFun = {1: [], 2: [], 3: []}
try:
    for costFun in costFunctionVals:
        nAnts = 1000
        nCycles = 10
        evapRate = 0.05
        tauMin = 0.15
        tauMax = 40
        sigma = 0.05
        errScale = 4
        strCost = "Lineal"
        if (costFun == 2): 
            strCost = "Exponencial" 
        elif (costFun == 3):
            strCost = "Pozo"
        f.write("nAnts: %i nCycles: %i evapRate: %.2f tauMin: %.2f tauMax: %i sigma:%.2f scale: %i costFun: %s\n\n" \
                % (nAnts, nCycles, evapRate, tauMin, tauMax, sigma, errScale, strCost))
        
        avgRuntime = .0
        avgSolsFound = .0
        for i in range(0, runsPerExperiment):
            allSols, elapsedTime =  runAlgorithm(True, scenario1, isElitist, \
                                    nAnts, nAnts, evapRate, tauMin, tauMax, \
                                    sigma, nCycles, errScale, costFun)
            avgRuntime += elapsedTime
            avgSolsFound += len(allSols)
            for sol in allSols:
                if not sol in uniqueSolsPerCostFun[costFun]:
                    uniqueSolsPerCostFun[costFun].append(sol)
            f.write("Run %i. Found %i sols in %.3f secs\n" % ((i+1), len(allSols), elapsedTime))
        
        avgRuntime /= runsPerExperiment
        avgSolsFound /= runsPerExperiment
        f.write("Average runtime : %.3f, avg sols found:%.3f\n" %(avgRuntime, avgSolsFound))
        uniqueSols = uniqueSolsPerCostFun[costFun]
        f.write("Found %i unique sols: \n" % len(uniqueSols))
        for uniqueSol in uniqueSols:
            f.write("\t%r\n" % uniqueSol)
        f.write("--------------------------------------------\n")
        
except Exception as e:
    print e, e.args
    f.close()
    
#~ try:
    #~ for costFunction in costFunctionVals:
        #~ for (nAnts, nCycles) in antsPerCycle:
            #~ for evapRate in evapRateVals:
                #~ for tauMin in tauMinVals:
                    #~ for tauMax in tauMaxVals:
                        #~ for sigma in sigmaVals:
                            #~ for errScale in errScaleVals:
                                #~ f.write("Case %i: nAnts: %i nCycles: %i evapRate: %.2f tauMin: %.2f tauMax: %i sigma:%.2f scale: %i costFun: %i\n" \
                                        #~ % (numCase, nAnts, nCycles, evapRate, tauMin, tauMax, sigma, errScale, costFunction))
                                #~ for i in range(0, runsPerExperiment):
                                    #~ print "Running experiment %i of %i for case %i" % (i, runsPerExperiment, numCase)
                                    #~ allSols, elapsedTime =  runAlgorithm(True, \
                                                #~ scenario1, isElitist, nAnts, \
                                                #~ nAnts, evapRate, tauMin, tauMax, \
                                                #~ sigma, nCycles, errScale, costFunction)
                                    #~ f.write("\nFound %i sols in %6.3f seconds" % (len(allSols), elapsedTime))
                                    #~ for sol in allSols:
                                        #~ f.write("\n %r" % sol)
                                        #~ if not sol in allDiffSolsFound:
                                            #~ allDiffSolsFound.append(sol)
                                #~ numCase += 1
                                #~ f.write("\n\n")
#~ except:
    #~ f.close()
        
f.close()
