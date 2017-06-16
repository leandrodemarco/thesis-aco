# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 19:54:08 2017

@author: leandro
"""
import scipy.special
import scipy.stats
import math

def binProb(i, n, p):
    """
        @Parameters: n -> number of trials
                     p -> probability of success
                     i -> test quantity
        @Returns: Bin(n,p)(i) P(X=i) for binomial(n,p) RV
    """    
    return scipy.special.binom(n,i) * (p**i) * ((1-p)**(n-i))
    
def poissonProb(i, lam):
    """
        @Params: lam -> Lambda parameter for the Poisson distribution
                 i -> test quantity
        @Returns: P(X=i) for Poisson(lam) RV
    """
    if (lam ** i == .0):
        # Then lam < 0
        return 0.
    
    try:
        term = (lam**i/math.factorial(i))
        res = math.e**(-lam) * term
    except OverflowError:
        # fac(i) too large, term -> 0
        res = .0        
     
    return res
        
    
def pValueBin(sample, top, totalAnts, prob):
    """
        * Computes T-statistic and p-value for a sample to test the null
        hypothesis 'sample has a bin(totalAnts, prob) distribution'
        @Parameters: sample: a dictionary {observedValues, frequency}
                     top: max value to check observedValues to avoid computing
                          irrelevant values
                    totalAnts and prob: binomial distribution parameters n,p
    """
    T = .0
    top = min(top, totalAnts)
    
    nRuns = 0
    for observedFreq in sample.values():
        nRuns += observedFreq
    
    for i in range(0, top):
        nObs = sample[i] if i in sample.keys() else 0                
            
        expected = nRuns * binProb(i, totalAnts, prob)
        term = (nObs-expected)**2 / expected         
        T += term
            
    p_val = scipy.stats.chi2.sf(T,top-1)
    
    return p_val, T
    
def pValuePoisson(sample, threshold, lam):
    """
        * Computes T-statistic and p-value for a sample to test the null
            hypothesis 'sample has a Poisson(lam) distribution'
        @Parameters: sample: a dictionary {observedValues, frequency}
                     threshold: upper limit: if threshold=T' then we calculate
                     P(X=0),..., P(X=T'-1) and P(X>=T')
                     lam: lambda parameter for Poisson distribution
    """
    T = .0
    
    nRuns = 0
    for observedFreq in sample.values():
        nRuns += observedFreq
    
    for i in range(0, threshold):
        nObs = sample[i] if i in sample.keys() else 0
        expected = nRuns * poissonProb(i, lam)
        term = (nObs - expected) ** 2 / expected
        
        print i, nObs, expected, nObs-expected, term
        
        T += term
     
    # Hay que ver si tenemos valores por arriba del "corte"
    # La probabilidad P(X>=threshold) = 1 - P(X<=threshold-1) = 
    # 1 - P(X=0) - ... - P(X=threshold-1)
    lowerAcum = .0
    for i in range(0, threshold):
        lowerAcum += poissonProb(i, lam)

    probAbove = 1 - lowerAcum
    
    expectedAbove = probAbove * nRuns    
    observationsAbove = 0
    
    for obsVals, obsFreqs in sample.items():
        if obsVals >= threshold:
            observationsAbove += obsFreqs
        
    T += (observationsAbove - expectedAbove) ** 2 / expectedAbove

    p_val = scipy.stats.chi2.sf(T, threshold-1)
    return p_val, T