#!/usr/bin/env python
#-*- encoding: utf-8 -*-

"""
    Este modulo implenta funciones unicamente para chequear si las 
    soluciones encontradas por el algoritmo principal efectivamente lo
    son. Su utilidad es pura y exclusivamente de debugging
"""

errMax = 0.025
targetG = 3.
targetQ = 6283.9478
targetOmega = 0.707

print "G debe estar entre: ", (targetG*(1-errMax)), " y: ", targetG*(1+errMax)
print "Q debe estar entre: ", (targetQ*(1-errMax)), " y: ", targetQ*(1+errMax)
print "W debe estar entre: ", (targetOmega*(1-errMax)), " y: ", targetOmega*(1+errMax) 

def qFactor(r1,r2,r3,c1,c2):
    fact_1 = (c2/c1)**(0.5)

    term_1 = ((r2*r3)**(0.5))/r1
    term_2 = (r3/r2)**(0.5)
    term_3 = (r2/r3)**(0.5)

    fact_2 = term_1 + term_2 + term_3
    return 1./(fact_1 * fact_2)
    

def checkSol(assignment):
    r1 = assignment['r1']
    r2 = assignment['r2']
    r3 = assignment['r3']
    c1 = assignment['c1']
    c2 = assignment['c2']
    
    G = r2/r1
    omega = 1./((r2*r3*c1*c2)**0.5)
    Q = qFactor(r1,r2,r3,c1,c2)
    
    print "G= ", G, " omega= ", omega, " Q= ", Q, "\n"
