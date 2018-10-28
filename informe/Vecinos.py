#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 17:14:32 2018

@author: leandrodemarcovedelago
"""

import ACOR
import Utils

use_log = False # Change this flag to use logarithmic version
best_r1_only = False
use_2_neighbours = True
a = ACOR.Acor('Vecinos', use_log)
u = Utils.Utils()

max_iters_per_r1 = 1 # Change it to run more ACOR iterations for each R1
output_dir = 'Vecinos/Logaritmico/' if use_log else 'Vecinos/Comun/'
filename = 'results_2.txt' if use_2_neighbours else 'results.txt'
f = open(output_dir + filename, 'w+')

sols = []
r1_vals = u.best_r1_sens if best_r1_only else u.res_vals
for R1 in r1_vals:
    for i in range(0, max_iters_per_r1):
        print 'Running iter %i for R1 = %i' % (i, R1)
        final_results = a.main_loop(R1)
        best_sol = final_results[:-1]
        cost = final_results[-1]
        if (use_log):
            best_sol = Utils.exp_list(best_sol)
        r2, r3, c4, c5 = best_sol[0], best_sol[1], best_sol[2], best_sol[3]
        curr_sols = u.fetch_neighbour_solutions(R1, r2, r3, c4, c5, 
                                                use_2_neighbours)
        for sol in curr_sols:
            if not sol in sols:
                f.write(u.full_solution_grouped_string(sol))
                sols.append(sol)

f.write('Hay %i soluciones' % len(sols))    
f.close() 