#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 22:32:46 2018

@author: leandrodemarcovedelago
"""

import ACOR
import Utils

use_log = True # Change this flag to use logarithmic version
best_r1_only = False
output_dir = 'ContinuoFijo/Logaritmico/' if use_log else 'ContinuoFijo/Comun/'

a = ACOR.Acor('ContinuoFijo', use_log)
u = Utils.Utils()

filename = 'results_short.txt' if best_r1_only else 'results_full.txt'
f = open(output_dir + filename, 'w+')

r1_vals = u.best_r1_sens if best_r1_only else u.res_vals
for R1 in r1_vals:
    print R1
    final_results = a.main_loop(R1)
    best_sol = final_results[:-1]
    cost = final_results[-1]
    if (use_log):
        best_sol = Utils.exp_list(best_sol)
    r2, r3, c4, c5 = best_sol[0], best_sol[1], best_sol[2], best_sol[3]
    isSol = u.is_sol(R1, r2, r3, c4, c5)
 
    is_sol_str = 'X\n' if isSol else '\n'
    f.write(u.full_solution_string(R1, r2, r3, c4, c5).rstrip() + ' ' 
            + is_sol_str)
    

f.close()