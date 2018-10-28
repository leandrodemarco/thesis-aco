#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from math import pi, sqrt
import time

def dominated_by(target_vector, candidate_vector):
    """
        Returns true if and only if candidate_vector components are all
        lower than those of target_vector, i.e candidate_vector dominates
        target_vector
    """
    sr1_target, sr2_target, sr3_target = target_vector
    sr1_cand, sr2_cand, sr3_cand = candidate_vector
    
    dominated = sr1_cand < sr1_target and sr2_cand < sr2_target and \
                sr3_cand < sr3_target
    return dominated

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

def find_sols(is_scenario1 = False, find_pareto_optimals = False):

    err = 0.005 if is_scenario1 else 0.025
        
    # Filter design specified desired values
    G = 3.0
    wp = 1000 * 2 * pi
    Q = 0.707

    # Acceptable min and max values
    wp_min = wp*(1-err)
    wp_max = wp*(1+err)

    G_min = G*(1-err)
    G_max = G*(1+err)

    Q_min = Q*(1-err)
    Q_max = Q*(1+err)
    Q_inv_max = 1./Q_min
    Q_inv_min = 1./Q_max

    """
        wp = 1/sqrt(r2*r3*c4*c5)
        Let w1 = 1/(r2*c4) and w2 = 1/(r3*c5)
        Then w2 = wp^2/w1 => (wp_min^2)/w1 < w2 < (wp_max^2)/w1 (1)
        
        For each possible w1 exists a {w2} such that condition (1) is satisfied
        
        G = r2/r1
        For each possible r1 there exists a set {r2} such that 
        G_max > G > G_min    (2)
    """

    res_bases = e96_values if is_scenario1 else e24_values
    cap_bases = e24_values if is_scenario1 else e12_values

    res_exps = [3,4,5]
    cap_exps = [-7,-8,-9]

    res_values = []
    for res_base in res_bases:
        for res_exp in res_exps:
            res_values.append(round(res_base * (10**res_exp), 10))
            
    cap_values = []
    for cap_base in cap_bases:
        for cap_exp in cap_exps:
            cap_values.append(round(cap_base * (10**cap_exp), 10))

    w_to_rc_map = {}
    w_vals = [] # w1 and w2 values are the same set of values (r1~r2, c4~c5)
    for r2 in res_values:
        for c4 in cap_values:
            w = 1./(r2*c4)
            
            if (w in w_to_rc_map.keys()):
                w_to_rc_map[w].append((r2,c4))
            else:
                w_to_rc_map[w] = [(r2,c4)]
            
            if (not w in w_vals):
                w_vals.append(w)

    w_vals.sort()

    constraint_1 = {} # Contains all (w1, {w2}) satisifying eq(1)
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
            constraint_1[w1] = possibles_w2
            

    # Each r1 has at most r2 in both scenarios
    constraint_2 =  [] # Contains all (r1, r2) pairs satisfying eq(2)
    for r1 in res_values:
        for r2 in res_values:
            G_r2 = r2/r1
            if (G_r2 > G_min and G_r2 < G_max):
                constraint_2.append((r1,r2))

    num_sols = 0
    solutions = []
    path_sols = []
    for r1, r2 in constraint_2:
        for w1, list_w2 in constraint_1.items():
            # Check if r2 "generates w1"
            l = w_to_rc_map[w1]
            generates = False
            for (r,c) in l:
                if (r == r2):
                    generates = True
                    break
                    
            if (generates):
                for w2 in list_w2:
                    for r3 in res_values:
                        # Check if r3 "generates w2"
                        l = w_to_rc_map[w2]
                        generates = False
                        for (r,c) in l:
                            if (r == r3):
                                generates = True
                                break
                        
                        if (generates):
                            Q_inv_r3 = (w1/w2)**0.5 * (1+r2/r1+r2/r3)
                            if (Q_inv_r3 > Q_inv_min and Q_inv_r3 < Q_inv_max):
                                c4, c5 = 1./(r2*w1), 1./(r3*w2)
                                gg = r2/r1
                                err_gg = 100*abs((G-gg)/G)
                                qq = 1./Q_inv_r3
                                err_qq = 100*abs((Q-qq)/Q)
                                omegap = sqrt(w1*w2)
                                err_omega = 100*abs((wp-omegap)/wp)
                                SR1 = qq*gg*sqrt(w1/w2)
                                SR2 = qq*sqrt(w1/w2)*abs(gg-1+r2/r3)/2
                                SR3 = qq*sqrt(w1/w2)*abs(gg+1-r2/r3)/2
                                ST = SR1+SR2+SR3
                                num_sols += 1
                                r1 = round(r1, 10)
                                r2 = round(r2, 10)
                                r3 = round(r3, 10)
                                c4 = round(c4, 10)
                                c5 = round(c5, 10)
                                solutions.append((r1,r2,r3,c4,c5,gg,err_gg,\
                                                  omegap, err_omega, qq,\
                                                  err_qq, SR1, SR2, SR3, ST))
                                path_sols.append({'r1':r1, 'r2':r2, 'r3': r3,\
                                                  'c1': c4, 'c2': c5})

    # Sort solutions according to ST
    sorted_sols = sorted(solutions, key = lambda t : (t[14], t[0], t[1],\
                                                      t[2], t[3], t[4], t[5],\
                                                      t[6], t[7], t[8], t[9],\
                                                      t[10], t[11], t[12],\
                                                      t[13]), reverse = False)
    
    optimals = None
    if (find_pareto_optimals):
        #Find pareto optimals with vector dominance          
        optimals = [sorted_sols[0]]
        for sol in sorted_sols[1:]:
            hasToAdd = True 
    
            for partial_opt in optimals:
                target = (partial_opt[11], partial_opt[12], partial_opt[13])
                candidate = (sol[11], sol[12], sol[13])
    
                if dominated_by(target, candidate):
                    # It's not optimal, remove it
                    optimals.remove(partial_opt)
                elif dominated_by(candidate, target):
                    # If we find just one value in current optimals that dominates
                    # candidate then we don't have to add candidate.
                    hasToAdd = False
                    break
    
            if hasToAdd:
                optimals.append(sol)

    return sorted_sols, optimals
        
start_time = time.time()
find_sols()
elapsed_time = time.time() - start_time
print elapsed_time
