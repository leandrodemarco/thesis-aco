#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 23:11:32 2018

@author: leandrodemarcovedelago

Corre la versión discreta pura del algoritmo
"""

import ACOR
import Utils

use_log = False # Change this flag to use logarithmic version
best_r1_only = False

output_dir = ('DiscretoPuro/Logaritmico/' if use_log 
              else 'DiscretoPuro/Comun/')
f = open(output_dir + 'results.txt', 'w+')

a = ACOR.Acor('DiscretoPuro', use_log)
u = Utils.Utils()

iterations_per_rval = 20
r1_vals = u.best_r1_sens if best_r1_only else u.res_vals
for R1 in r1_vals:
    done = False
    for i in range(0, iterations_per_rval):
        print 'Running iter %i for R1: %i' % (i+1, R1)
        if done:
            break
        best_sol = a.main_loop(R1)
        r2, r3, c4, c5 = best_sol[0], best_sol[1], best_sol[2], best_sol[3]
        sens = u.get_sol_info(R1, r2, r3, c4, c5)[0]
        isSol = u.is_sol(R1, r2, r3, c4, c5)
        if (isSol):
            done = True
            f.write('Iteraciones: ' +str(i+1))
            f.write(u.full_solution_string(R1, r2, r3, c4, c5))
    if not done:
        f.write('No hallo soluciones para R1: ' + str(R1) + '\n')
            
f.close()