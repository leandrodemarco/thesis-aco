#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from math import *
from operator import itemgetter
import sys
import time

def dominatedBy(targetVector, candidateVector):
    """
        @Params:
            targetVector: vector to see if it's dominated by
                          candidateVector
            Each vector contains SR1, SR2 and SR3
        @Returns:
            True if candidateVector dominates targetVector False otherwise
        @Note:
            candidateVector dominates vector targetVector if all elements 
            from it are lower than targetVector elementwise 
    """
    SR1target, SR2target, SR3target = targetVector
    SR1cand, SR2cand, SR3cand = candidateVector
    dominated = SR1cand < SR1target and SR2cand < SR2target and \
                SR3cand < SR3target
                
    return dominated
    

start_time = time.time()

e12_values = [1., 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

e24_values = [1., 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2, 2.2, 2.4, 2.7, 3, \
              3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, \
              9.1]
              
e96_values = [1., 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24,\
              1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, \
              1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, \
              1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, \
              2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, \
              3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, \
              3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, \
              4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, \
              5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, \
              7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, \
              8.87, 9.09, 9.31, 9.53, 9.76]

isScenario1 = True

err = 0.025
if (isScenario1): err=0.005
    
# Constantes especificadas en el diseño del filtro
G = 3.0
#wp = 6283.9478
wp = 1000*2*pi
Q = 0.707
#Q = 1/sqrt(2.0)

# Margen de error
wp_min = wp*(1-err)
wp_max = wp*(1+err)
#print wp_min, wp_max

G_min = G*(1-err)
G_max = G*(1+err)

Q_min = Q*(1-err)
Q_max = Q*(1+err)
Q_inv_max = 1./Q_min
Q_inv_min = 1./Q_max

all_solutions = []

"""
    wp = 1/sqrt(r2*r3*c4*c5)
    Sean w1 = 1/(r2*c4) y w2 = 1/(r3*c5)
    Entonces w2 = wp^2/w1 => (wp_min^2)/w1 < w2 < (wp_max^2)/w1 (1)
    
    Para cada w1 posible existe un {w2} tq se satisface la cond (1)
    
    G = r2/r1
    Para cada r1 posible existe un {r2} tq G_max > G > G_min    (2)
"""

res_bases = e24_values
if (isScenario1): res_bases = e96_values

cap_bases = e12_values
if (isScenario1): cap_bases = e24_values

res_exps = [3,4,5]
cap_exps = [-7,-8,-9]

res_values = []
for res_base in res_bases:
    for res_exp in res_exps:
        res_values.append(res_base * (10**res_exp))
        
cap_values = []
for cap_base in cap_bases:
    for cap_exp in cap_exps:
        cap_val = cap_base * (10**cap_exp)
        cap_values.append(cap_base * (10**cap_exp))

wToRCMap = {}
w_vals = [] # w1 and w2 values are the same set of values (r1~r2, c4~c5)
for r2 in res_values:
    for c4 in cap_values:
        w = 1./(r2*c4)
        w = round(w,5)
        
        if (w in wToRCMap.keys()):
            wToRCMap[w].append((r2,c4))
        else:
            wToRCMap[w] = [(r2,c4)]
        
        if (not w in w_vals):
            w_vals.append(w)

w_vals.sort()

constraint1 = {} # Contains all (w1, {w2}) satisifying eq(1)
wp_max_squared = wp_max**2
wp_min_squared = wp_min**2

for w1 in w_vals:
    possibles_w2 = []
    for w2 in w_vals:
        low_end = wp_min_squared/w1
        high_end = wp_max_squared/w1
        if (w2 > low_end and w2 < high_end):
            possibles_w2.append(w2)
    if (len(possibles_w2) > 0):
        constraint1[w1] = possibles_w2
        

# Cada r1 tiene a lo sumo un r2 en ambos escenarios
constraint2 =  [] # Contains all (r1, r2) pairs satisfying eq(2)
for r1 in res_values:
    for r2 in res_values:
        G_r2 = r2/r1
        if (G_r2 > G_min and G_r2 < G_max):
            constraint2.append((r1,r2))

"""print       
print "  i    R1    R2     R3    C4      C5      G    Eg    W_p    Ew    Q    Eq    SR1    SR2    SR3  STOTAL"
print"""       
constraint3 = {}
numSols = 0
solutions = []
for r1, r2 in constraint2:
    for w1, list_w2 in constraint1.items():
        # Check if r2 "generates w1"
        l = wToRCMap[w1]
        generates = False
        for (r,c) in l:
            if (r == r2):
                generates = True
                break
                
        if (generates):
            for w2 in list_w2:
                for r3 in res_values:
                    # Check if r3 "generates w2"
                    l = wToRCMap[w2]
                    generates = False
                    for (r,c) in l:
                        if (r == r3):
                            generates = True
                            break
                    
                    if (generates):
                        Q_inv_r3 = (w1/w2)**0.5 * (1+r2/r1+r2/r3)
                        if (Q_inv_r3 > Q_inv_min and Q_inv_r3 < Q_inv_max):
                            #print r2/r1, (w1*w2)**0.5, 1./Q_inv_r3
                            c4, c5 = 1./(r2*w1), 1./(r3*w2)
#                           c4, c5 = round(c4, 12), round(c5,12)
                            gg = r2/r1
                            errgg = 100*abs((G-gg)/G)
                            qq = 1/Q_inv_r3
                            errqq = 100*abs((Q-qq)/Q)
                            omegap = sqrt(w1*w2)
                            erromega = 100*abs((wp-omegap)/wp)
                            SR1 = qq*gg*sqrt(w1/w2)
                            SR2 = qq*sqrt(w1/w2)*abs(gg-1+r2/r3)/2
                            SR3 = qq*sqrt(w1/w2)*abs(gg+1-r2/r3)/2
                            ST = SR1+SR2+SR3
                            numSols=numSols+1
                            solutions.append((r1,r2,r3,c4,c5,gg,errgg,omegap, erromega, qq, errqq, SR1, SR2, SR3, ST))
#                           print numSols,r1,r2,r3,c4,c5,gg,omegap
                            """print ("%4d %5d %6d %5d %7.1e %7.1e %5.3f %3.2f %7.2f %3.2f %5.3f %3.2f %6.4f %6.4f %6.4f %6.4f" % \
                            (numSols,r1,r2,r3,c4,c5,gg,errgg,omegap,erromega,qq,errqq,\
                            SR1,SR2,SR3,ST))"""

"""
Find pareto optimals with vector dominance
"""
sorted_sols = sorted(solutions, key = lambda t : (t[14], t[0], t[1], t[2], t[3], t[4], t[5], \
                t[6], t[7], t[8], t[9], t[10], t[11], t[12], t[13]), reverse = False)
                
optimals = [sorted_sols[0]]
for sol in sorted_sols[1:]:
    hasToAdd = True 

    for partial_opt in optimals:
        target = (partial_opt[11], partial_opt[12], partial_opt[13])
        candidate = (sol[11], sol[12], sol[13])

        if dominatedBy(target, candidate):
            # Remove partial_opt from optimals
            optimals.remove(partial_opt)
        elif dominatedBy(candidate, target):
            # If we find just one value in current optimals that dominates
            # candidate then we don't have to add candidate.
            hasToAdd = False
            break

    if hasToAdd:
        optimals.append(sol)

print len(optimals)

""" END Pareto optimals search """

writeSols = True
if (writeSols):
    filename = 'SortedSolsEsc1.txt' if isScenario1 else 'SortedSolsEsc2.txt'                    
    f = open(filename, 'w+')
    title = 'Escenario 1' if isScenario1 else 'Escenario 2'

    f.write('Numero de soluciones: %i\n\n' % numSols)
    f.write('Los valores de cada columna corresponden a R1, R2, R3, C4, C5, G, err(G), wp, err(wp), Qp, Err(Qp),SR1, SR2, SR3 y ST\n\n')

    f.write('   R1     R2    R3     C4     C5     G   err(G)    wp   err(wp)  Qp   Err(Qp)\
      SR1     SR2    SR3    ST\n')

    for sol in sorted_sols:
        (r1,r2,r3,c4,c5,gg,errgg,omegap,erromega,qq,errqq, SR1,SR2,SR3,ST) = sol
        sol_str = "%5d %6d %5d %7.1e %7.1e %5.3f %3.4f %7.2f %3.4f %5.4f %3.4f %6.4f %6.4f %6.4f %6.4f" % \
            (r1,r2,r3,c4,c5,gg,errgg,omegap,erromega,qq,errqq,\
            SR1,SR2,SR3,ST)
        
        if sol in optimals:
            sol_str += " X\n"
        else:
            sol_str += "\n"
        
        f.write(sol_str)
        
    f.write("\n--- %s seconds ---" % (time.time() - start_time))
        
    f.close()        
