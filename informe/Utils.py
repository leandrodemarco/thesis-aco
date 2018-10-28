#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 21:03:10 2018

@author: leandrodemarcovedelago

Define constants and functions used in every variant of the algorithm we have
implemented
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import csv
from bisect import bisect_left
from itertools import product

"""
    Module helper functions
"""
def format_e(n):
    a = '%E' % n
    return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]
       

def wheel_selection(P):
    r = np.random.uniform()
    C = np.cumsum(P)
    for i in range(0, len(C)):
        if C[i] > r:
            break
        
    j = max(0,i-1)
    return j

def exp_list(l):
    return map(lambda x: math.exp(x), l)

def _solution_string(r1, r2, r3, c4, c5):
    return str(r1) + ' ' + str(r2) + ' ' + str(r3) + ' ' + str(c4) + ' ' \
           + str(c5)

class Utils:
    def __init__(self, is_scenario1 = False, g_wgt = 100000., \
                 sens_wgt = 1000., light_wgt = 100.):
        
        self.is_scenario1 = is_scenario1
        
        # Weights for G, Sens and light for wp and Q
        self.g_wgt = g_wgt
        self.sens_wgt = sens_wgt
        self.light_wgt = light_wgt
        
        self._setup_resistors_and_capacitors_values()
        self._setup_objective_values()
        self._setup_err_and_threshold_values()
        self._setup_ACOR_params()
    
    """
        Filter components possible and desired values. Error definitions
    """
    def _setup_resistors_and_capacitors_values(self):
        e12_values = [1., 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, \
                      8.2]
        
        e24_values = [1., 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2., 2.2, 2.4, 2.7, \
                      3., 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, \
                      8.2, 9.1]
        
        e96_values = [1., 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, \
                      1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, \
                      1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, \
                      1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, \
                      2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, \
                      2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, \
                      3.65, 3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, \
                      4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, \
                      5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, \
                      6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, \
                      8.66, 8.87, 9.09, 9.31, 9.53, 9.76]
        
        res_exps = [3,4,5]
        cap_exps = [-7,-8,-9]
        
        res_series = e96_values if self.is_scenario1 else e24_values
        cap_series = e24_values if self.is_scenario1 else e12_values
        
        self.res_vals = [x*(10**y) for x in res_series for y in res_exps]
        self.cap_vals = [x*(10**y) for x in cap_series for y in cap_exps]
        self.res_vals.sort()
        self.cap_vals.sort()
        
        log_fun = lambda x: math.log(x)
        self.log_res_vals = map(log_fun, self.res_vals)
        self.log_cap_vals = map(log_fun, self.cap_vals)
        
        self.cap_min, self.cap_max = self.cap_vals[0], self.cap_vals[-1]
        self.res_min, self.res_max = self.res_vals[0]-1, self.res_vals[-1]+1
        
        # Holds best 5 values from exhaustive solution w.r.t Sens
        self.best_r1_sens = [11000., 3600., 36000., 12000., 3300.]
        
    """
        ACOR SETUP
    """
        
    def _setup_objective_values(self):
        self.obj_g = 3.0
        self.obj_wp = 1000*2*math.pi
        self.obj_q = 1/math.sqrt(2.0)
        self.obj_invq = 1/self.obj_q
        self.obj_sens = 0.75
        
    def _setup_err_and_threshold_values(self):
        err = 0.005 if self.is_scenario1 else 0.025
        self.max_err = err
        self.g_max = (1+err) * self.obj_g
        self.g_min = (1-err) * self.obj_g
        self.wp_max = (1+err) * self.obj_wp
        self.wp_min = (1-err) * self.obj_wp
        self.q_max = (1+err) * self.obj_q
        self.q_min = (1-err) * self.obj_q
        
    def _setup_ACOR_params(self):
        self.archive_size = 10
        self.sample_size = 40
        self.max_iterations = 200
        self.intensification_factor = 0.5 # Intensification factor
        self.zeta = 1.0 # Deviation-Distance ratio
        
    """
        Functions for getting information about a given assignment 
        (r1, r2, r3, c4, c5)
    """    
    def get_sol_info_grouped(self, grouped_solution):
        r1, r2, r3, c4, c5 = grouped_solution
        return self.get_sol_info(r1, r2, r3, c4, c5)
    
    def get_sol_info(self, r1, r2, r3, c4, c5):
        a = r1/r2
        b = r1/r3
        g = 1/a
        sens = (2 + abs(1-a+b) + abs(1+a-b))/(2*(1+a+b))
        omega = math.sqrt(a*b/(c4*c5))/r1
        invq = math.sqrt(c5/(c4*a*b))*(1+a+b)
        
        return (sens, g, 1./invq, omega)
    
    def is_soft_sol(self, r1, r2, r3, c4, c5):
        """
            Given an assignment for each filter component checks if it's
            a soft solution, i.e if it satisfies every constraint except
            maybe the sens < 1 constraint
        """
        sens, g, q, wp = self.get_sol_info(r1,r2,r3,c4,c5)
        g_ok = g < self.g_max and g > self.g_min
        wp_ok = wp < self.wp_max and wp > self.wp_min
        q_ok = q < self.q_max and q > self.q_min
        
        return g_ok and wp_ok and q_ok
    
    def is_sol_grouped(self, grouped_solution):
        r1, r2, r3, c4, c5 = grouped_solution
        return self.is_sol(r1, r2, r3, c4, c5)

    def is_sol(self, r1, r2, r3, c4, c5):
        """
            Given an assignment for each filter component checks if it's
            a valid solution, i.e if it satisfies every constraint
        """
        sens, g, q, omega = self.get_sol_info(r1,r2,r3,c4,c5)
        sens_ok = sens < 1
        return sens_ok and self.is_soft_sol(r1, r2, r3, c4, c5)
    
    def err_g(self, g):
        return 100 * abs(g - self.obj_g) / self.obj_g
    
    def err_wp(self, wp):
        return 100 * abs(wp - self.obj_wp) / self.obj_wp
    
    def err_q(self, q):
        return 100 * abs(q - self.obj_q) / self.obj_q
    
    def cost(self, assignment, use_log = False, fixed_R1 = None):
        #print assignment
        if (use_log):
            # assignment holds the logarithms of the components not their
            # proper value
            assignment = exp_list(assignment)
            
        if (fixed_R1 != None):
            r1 = fixed_R1
            r2,r3,c4,c5 = assignment
        else:
            r1, r2, r3, c4, c5 = assignment
        
        r1_range_OK = r1 > self.res_min and r1 < self.res_max
        r2_range_OK = r2 > self.res_min and r2 < self.res_max
        r3_range_OK = r3 > self.res_min and r3 < self.res_max
        c4_range_OK = c4 > self.cap_min and c4 < self.cap_max
        c5_range_OK = c5 > self.cap_min and c5 < self.cap_max
        if all([r1_range_OK, r2_range_OK, r3_range_OK, c4_range_OK, 
               c5_range_OK]):
            a = r1/r2
            b = r1/r3
            sol_g = 1/a
            sol_sens = (2 + abs(1-a+b) + abs(1+a-b))/(2*(1+a+b))
            sol_w = math.sqrt(a*b/(c4*c5))/r1
            sol_invq = math.sqrt(c5/(c4*a*b))*(1+a+b)
            
            g_cost = self.g_wgt * (sol_g - self.obj_g) ** 2
            sens_cost = self.sens_wgt * sol_sens**2
            #print sol_w, self.obj_wp, r1
            wp_cost = self.light_wgt * (math.log(sol_w/self.obj_wp))**2
            q_cost = self.light_wgt * (math.log(sol_invq/self.obj_invq))**2
            
            return sens_cost + g_cost + wp_cost + q_cost
        else:
            # Heavily penalize configurations that do not lie in range
            return 1.0e11
        
    """
        Get sol info as string for printing
    """
    def full_solution_string(self, r1, r2, r3, c4, c5):
        sens, g, Q, wp = self.get_sol_info(r1, r2, r3, c4, c5)
        sol_str = _solution_string(r1, r2, r3, c4, c5)
        sol_str += str(sens) + ' ErrG: ' + str(self.err_g(g)) + ' '
        sol_str += 'ErrQ: ' + str(self.err_q(Q)) + ' ErrWp: ' \
                     + str(self.err_wp(wp)) + '\n'
        return sol_str
    
    def full_solution_grouped_string(self, solution):
        r1, r2, r3, c4, c5 = solution
        return self.full_solution_string(r1, r2, r3, c4, c5)
        
    """
        Neighbouring
    """
    def find_discrete_neighbour_components(self, comp_val, is_resistor,
                                           find_2 = False):
        """
            Given a component (resistor or capacitor) value, returns a list
            holding the closest admisible values according to the E industrial
            series. List may have 1 element (if comp_val is lower than lowest
            admisible value or greater than highest one) or 2 elements (any
            other case where comp_val lies between two admisible values)
        """
        target_arr = self.res_vals if is_resistor else self.cap_vals
        idx = bisect_left(target_arr, comp_val)
        if (idx == 0):
            if not find_2:
                return [target_arr[0]]
            else:
                return [target_arr[0], target_arr[1]]
        if (idx == len(target_arr)):
            if not find_2:
                return [target_arr[-1]]
            else:
                return [target_arr[-1], target_arr[-2]]
        
        if not find_2:
            return [target_arr[idx-1], target_arr[idx]]
        else:
            lower = [target_arr[idx-1]]
            if (idx > 1):
                lower.append(target_arr[idx-2])
            higher = [target_arr[idx]]
            if (idx + 1 < len(target_arr)):
                higher.append(target_arr[idx+1])
            return lower + higher
    
    def fetch_neighbour_solutions(self, R1, r2, r3, c4, c5, find_2 = False):
        solutions = []
        r1_cands = self.find_discrete_neighbour_components(R1, True, find_2)
        r2_cands = self.find_discrete_neighbour_components(r2, True, find_2)
        r3_cands = self.find_discrete_neighbour_components(r3, True, find_2)
        c4_cands = self.find_discrete_neighbour_components(c4, False, find_2)
        c5_cands = self.find_discrete_neighbour_components(c5, False, find_2)
        cand_solutions = product(r1_cands, r2_cands, r3_cands, c4_cands, 
                                 c5_cands)
        for cand_sol in cand_solutions:
            if self.is_sol_grouped(cand_sol) and not cand_sol in solutions:
                solutions.append(list(cand_sol))
        return solutions

class PlotingUtils:
    def __init__(self, bests_arr, output_dir = None):
        self.output_dir_path = output_dir if output_dir != None else ""
        self.r1_filename = self.output_dir_path + 'R1.txt'
        self.r2_filename = self.output_dir_path + 'R2.txt'
        self.r3_filename = self.output_dir_path + 'R3.txt'
        self.c4_filename = self.output_dir_path + 'C4.txt'
        self.c5_filename = self.output_dir_path + 'C5.txt'
        self.cost_filename = self.output_dir_path + 'COST.txt'
        
        self.full_fig_filename = self.output_dir_path + 'cc-full.png'
        self.cost_fig_filename = self.output_dir_path + 'cc-costo.png'
        self.r1_fig_filename = self.output_dir_path + 'cc-r1.png'
        self.r2_fig_filename = self.output_dir_path + 'cc-r2.png'
        self.r3_fig_filename = self.output_dir_path + 'cc-r3.png'
        self.c4_fig_filename = self.output_dir_path + 'cc-c4.png'
        self.c5_fig_filename = self.output_dir_path + 'cc-c5.png'
        
        self.best_r1 = bests_arr[0]
        self.best_r2 = bests_arr[1]
        self.best_r3 = bests_arr[2]
        self.best_c4 = bests_arr[3]
        self.best_c5 = bests_arr[4]
        self.best_cost = bests_arr[5]
        
    def plot_cost_and_vars(self):
        max_iterations = Utils().max_iterations
        plt.figure(figsize=(15,15))

        plt.subplot(3,2,1)
        plt.yscale('log')
        plt.plot(range(1, max_iterations+1), self.best_r1)
        plt.ylabel('R1')
        
        plt.subplot(3,2, 2)
        plt.yscale('log')
        plt.plot(range(1, max_iterations+1), self.best_c4)
        plt.ylabel('C4')
        
        plt.subplot(3,2, 3)
        plt.yscale('log')
        plt.plot(range(1, max_iterations+1), self.best_r2)
        plt.ylabel('R2')
        
        plt.subplot(3,2, 4)
        plt.yscale('log')
        plt.plot(range(1, max_iterations+1), self.best_c5)
        plt.ylabel('C5')
        
        plt.subplot(3,2, 5)
        plt.yscale('log')
        plt.plot(range(1, max_iterations+1), self.best_r3)
        plt.ylabel('R3')
        
        plt.subplot(3, 2, 6)
        plt.yscale('log')
        plt.plot(range(1, max_iterations+1), self.best_cost)
        plt.ylabel('Costo')
        
        print self.cost_fig_filename
        plt.savefig(self.full_fig_filename)
        plt.close()
        #plt.show()
        
        fr1 = open(self.r1_filename, 'w+')
        fr2 = open(self.r2_filename, 'w+')
        fr3 = open(self.r3_filename, 'w+')
        fc4 = open(self.c4_filename, 'w+')
        fc5 = open(self.c5_filename, 'w+')
        fcost = open(self.cost_filename, 'w+')
        for i in range(0, max_iterations):
            r1 = self.best_r1[i]
            r2 = self.best_r2[i]
            r3 = self.best_r3[i]
            c4 = self.best_c4[i]
            c5 = self.best_c5[i]
            costo = self.best_cost[i]
            fr1.write("%3d,%7.4f\n" % (i,r1))
            fr2.write("%3d,%7.4f\n" % (i,r2))
            fr3.write("%3d,%7.4f\n" % (i,r3))
            fc4.write("%3d,%9.4e\n" % (i,c4))
            fc5.write("%3d,%9.4e\n" % (i,c5))
            fcost.write("%3d,%9.4e\n" % (i,costo))
        
        fr1.close()
        fr2.close()
        fr3.close()
        fc4.close()
        fc5.close()
        fcost.close()
        
    def generate_png_files(self):
        dx = 8.5/2.54
        dy = 5.5/2.54
        
        x = []
        y = []
        csvfile = open(self.cost_filename,'r')
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(int(row[0]))
            y.append(float(row[1]))

        plt.figure(figsize=(dx,dy))
        plt.yscale('log')
        plt.tight_layout()
        plt.plot(range(0, max(x)+1), y)
        plt.savefig(self.cost_fig_filename)
        plt.close()
        
        x = []
        y = []
        csvfile = open(self.r1_filename,'r')
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(int(row[0]))
            y.append(float(row[1]))
        plt.figure(figsize=(dx,dy))
        plt.axis([0, max(x)+1, min(y), max(y)])
        plt.yscale('log')
        plt.tight_layout()
        plt.plot(range(0, max(x)+1), y)
        plt.savefig(self.r1_fig_filename)
        #plt.show()
        plt.close()
        
        x = []
        y = []
        csvfile = open(self.r2_filename,'r')
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(int(row[0]))
            y.append(float(row[1]))
        plt.figure(figsize=(dx,dy))
        plt.axis([0, max(x)+1, min(y), max(y)])
        plt.yscale('log')
        plt.tight_layout()
        plt.plot(range(0, max(x)+1), y)
        plt.savefig(self.r2_fig_filename)
        plt.close()
        
        x = []
        y = []
        csvfile = open(self.r3_filename,'r')
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(int(row[0]))
            y.append(float(row[1]))
        plt.figure(figsize=(dx,dy))
        plt.axis([0, max(x)+1, min(y), max(y)])
        plt.yscale('log')
        plt.tight_layout()
        plt.plot(range(0, max(x)+1), y)
        plt.savefig(self.r3_fig_filename)
        plt.close()
        
        x = []
        y = []
        csvfile = open(self.c4_filename,'r')
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(int(row[0]))
            y.append(float(row[1]))
        plt.figure(figsize=(dx,dy))
        plt.axis([0, max(x)+1, min(y), max(y)])
        plt.yscale('log')
        plt.tight_layout()
        plt.plot(range(0, max(x)+1), y)
        plt.savefig(self.c4_fig_filename)
        plt.close()
        
        x = []
        y = []
        csvfile = open(self.c5_filename,'r')
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(int(row[0]))
            y.append(float(row[1]))
        plt.figure(figsize=(dx,dy))
        plt.axis([0, max(x)+1, min(y), max(y)])
        plt.yscale('log')
        plt.tight_layout()
        plt.plot(range(0, max(x)+1), y)
        plt.savefig(self.c5_fig_filename)
        plt.close()
