#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 18:23:12 2018

@author: leandrodemarcovedelago
"""

import ACOR
import Utils

use_log = True # Change this flag to use logarithmic version
output_dir = ('ContinuoLibre/Logaritmico/' if use_log 
              else 'ContinuoLibre/Comun/')
f = open(output_dir + 'results.txt', 'w+')

a = ACOR.Acor('ContinuoLibre', use_log)
u = Utils.Utils()
final_results = a.main_loop()
best_sol = final_results[:-1]
cost = final_results[-1]

if (use_log):
    best_sol = Utils.exp_list(best_sol)
    
r1, r2, r3, c4, c5 = best_sol[:5]
f.write(u.full_solution_string(r1, r2, r3, c4, c5))
f.close()

plot = True
if (plot):
    best_r1 = Utils.exp_list(a.best_r1) if use_log else a.best_r1
    best_r2 = Utils.exp_list(a.best_r2) if use_log else a.best_r2
    best_r3 = Utils.exp_list(a.best_r3) if use_log else a.best_r3
    best_c4 = Utils.exp_list(a.best_c4) if use_log else a.best_c4
    best_c5 = Utils.exp_list(a.best_c5) if use_log else a.best_c5
    best_cost = a.best_cost
    plot_utils = Utils.PlotingUtils([best_r1, best_r2, best_r3, best_c4,
                                     best_c5, best_cost], output_dir)
    plot_utils.plot_cost_and_vars()
    plot_utils.generate_png_files()
    