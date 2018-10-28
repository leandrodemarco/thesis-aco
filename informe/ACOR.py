#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 21:55:06 2018

@author: leandrodemarcovedelago
"""

import numpy as np
import numpy.matlib as npmatlib
import math
import Utils

class Acor:
    def __init__(self, alg_variant, uses_log):
        """
            * alg_variant should be one of the following strings: 
                'ContinuoLibre', 'ContinuoFijo', 'Vecinos', 'DiscretoPuro'
            * uses_log: boolean indicating whether or not to use logarithm
                        of components instead of their regular value
        """
        self.alg_variant = alg_variant
        self.uses_log = uses_log
        self.utils = Utils.Utils()
        self.num_dimensions = 5 if alg_variant == 'ContinuoLibre' else 4
        self.num_resistors = 3 if alg_variant == 'ContinuoLibre' else 2
        
    def _calc_comp_val_discrete(self, means, sigmas, comp_idx, p):
        """
            This function is used to discretize the value of a filter component
            from a continuous calculalted value by ACOR when using the
            variant 'DiscretoPuro'
            * means: array of means
            * sigmas: array of standard deviations
            * comp_idx: index of the component to discretize
            * p: probabilities array
        """
        i = comp_idx
        res_vals, cap_vals = self.utils.res_vals, self.utils.cap_vals
        log_res_vals = self.utils.log_res_vals
        log_cap_vals = self.utils.log_cap_vals
        
        # Select Gaussian Kernel
        l = Utils.wheel_selection(p)
        # Generate Gaussian Random Variable
        aux = means[l][i] + sigmas[l][i] * np.random.randn()
        is_resistor = i < self.num_resistors
        if (is_resistor and not self.uses_log):
            vals_to_use = res_vals
        elif (is_resistor and self.uses_log):
            vals_to_use = log_res_vals
        elif (not is_resistor and not self.uses_log):
            vals_to_use = cap_vals
        else:
            vals_to_use = log_cap_vals
        
        idx = np.abs(vals_to_use - aux).argmin()
        return vals_to_use[idx]
    
    def _initialize_archive(self, R1):
        res_min, res_max = self.utils.res_min, self.utils.res_max
        cap_min, cap_max = self.utils.cap_min, self.utils.cap_max
        num_dim = self.num_dimensions
        archive_size = self.utils.archive_size
        cost = self.utils.cost
        
        empty_ant = np.empty([num_dim + 1])
        archive = npmatlib.repmat(empty_ant, archive_size, 1)
        
        for i in range(0, archive_size):
            for j in range(0, num_dim + 1):
                if (j < self.num_resistors):
                    # Resistor
                    low = math.log(res_min) if self.uses_log else res_min
                    high = math.log(res_max) if self.uses_log else res_max
                    archive[i][j] = np.random.uniform(low, high)
                elif (j < num_dim):
                    # Capacitor
                    low = math.log(cap_min) if self.uses_log else cap_min
                    high = math.log(cap_max) if self.uses_log else cap_max
                    archive[i][j] = np.random.uniform(low, high) 
                else:
                    # Cost
                    archive[i][j] = cost(archive[i][0:num_dim], self.uses_log,
                                         R1)
                    
        return archive
                
    def main_loop(self, R1 = None):
        archive_size = self.utils.archive_size        
        num_dim = self.num_dimensions
        max_iterations = self.utils.max_iterations
        int_factor = self.utils.intensification_factor
        zeta = self.utils.zeta
        sample_size = self.utils.sample_size
        cost = self.utils.cost
        use_log = self.uses_log
                
        # Hold data of evolution for cost and variables through execution
        self.best_cost = np.zeros([max_iterations])
        self.best_r1 = np.zeros([max_iterations])
        self.best_r2 = np.zeros([max_iterations])
        self.best_r3 = np.zeros([max_iterations])
        self.best_c4 = np.zeros([max_iterations])
        self.best_c5 = np.zeros([max_iterations])
        
        archive = self._initialize_archive(R1)
        archive = archive[archive[:,num_dim].argsort()]
        
        # Weights array
        w = np.empty([archive_size])
        for l in range(0, archive_size):
            f_factor = 1/(math.sqrt(2*math.pi)*int_factor*archive_size)
            s_factor = math.exp(-0.5*(l/(int_factor*archive_size))**2)
            w[l] = f_factor * s_factor
        
        # Selection probabilities
        p = w / np.sum(w)
        
        # ACOR Main Loop
        empty_ant = np.empty([num_dim + 1])
        for it in range(0, max_iterations):
            # Means
            s = np.zeros([archive_size, num_dim])
            for l in range(0, archive_size):
                s[l] = archive[l][0:num_dim]
            
            # Standard deviations
            sigma = np.zeros([archive_size, num_dim])
            for l in range(0, archive_size):
                D = 0
                for r in range(0, archive_size):
                    D += abs(s[l]-s[r])
                sigma[l] = zeta * D / (archive_size - 1)
                
            # Create new population array
            new_population = np.matlib.repmat(empty_ant, sample_size, 1)
            # Initialize solution for each new ant
            for t in range(0, sample_size):
                new_population[t][0:num_dim] = np.zeros([num_dim])
                
                for i in range(0, num_dim):
                    if (self.alg_variant == 'DiscretoPuro'):
                        comp_val = self._calc_comp_val_discrete(s, sigma, i, p)
                        new_population[t][i] = comp_val
                    else:
                        # Select Gaussian Kernel
                        l = Utils.wheel_selection(p)
                        # Generate Gaussian Random Variable
                        new_population[t][i] = (s[l][i] 
                                               + sigma[l][i]*np.random.randn())

                # Evaluation of built solution
                filter_comps = new_population[t][0:num_dim]
                new_population[t][num_dim] = cost(filter_comps, use_log, R1)
                
            # Merge old population (archive) with new one
            merged_pop = np.concatenate([archive, new_population])
            # And sort it again
            merged_pop = merged_pop[merged_pop[:,num_dim].argsort()]
            # Store the bests in the archive and update best sol
            archive = merged_pop[:archive_size]
            best_sol = archive[0][0:num_dim] # Current best solution, NO cost
            self.best_cost[it] = archive[0][num_dim] # Current best cost
            self.best_r1[it] = R1 if R1 != None else best_sol[0]
            if self.uses_log and R1 != None:
                self.best_r1[it] = math.log(R1)
            self.best_r2[it] = best_sol[0] if R1 != None else best_sol[1]
            self.best_r3[it] = best_sol[1] if R1 != None else best_sol[2]
            self.best_c4[it] = best_sol[2] if R1 != None else best_sol[3]
            self.best_c5[it] = best_sol[3] if R1 != None else best_sol[4]
        
        return archive[0] # Best population and cost
