# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 11:23:06 2021

PDOPT Analysis using new HEPS code, an updated version of the code from
 Dec. 2020 with a Gas Turbine Map and Boeing FuelFlow2 method for estimating
 NOx and CO emissions with data from https://doi.org/10.1016/j.trd.2018.01.019. 

The mission is the reference design mission from FP50, flight from
 Edimbourgh to Dublin with alternate to Belfast, defined in the 
 data/mission.csv file. 

The architecture is fixed with parameters defined in the 
 data/architecture.json file.
 
Objectives and Constraints are pulled from the TLARs of FP50, as presented
 in https://www.mdpi.com/2226-4310/8/3/61/htm. 
 
Assumptions for this set of experiments:
    - The aircraft is retrofitted, i.e. we target a MTOM that is no larger
      than the reference aircraft (with some added margin).
    - Empty weight is assumed constant, the GT is the same as reference (PW127).
    - The battery are assumed to be removable, hence we want to minimize TOM.
    - Descent phase runs on prime mover only, it is expected to have some form
      electrical storage charging (not modeled here).
    - Some flight conditions are lumped (TO and Climbout, Landing and Final).
    - Ground movements are ignored.


Architecture: Parallel (FP50 Type 2)

Shared Objective: 
    - Minimize Fuel Consumption (CO2)
    - Minimize NOx
                    
Shared Constraints, encoded also as Step 1 Requirements: 
    - TOM < 20000 kg (MTOM)

@author: s345001

This file contains the Experiment definition and shared data
which is imported in each individual file that runs the tests.
"""

import json
import sys
import pickle as pk
import argparse

from os.path import exists

import pandas as pd
import numpy as np
from tqdm import tqdm

from pdopt.data import DesignSpace, ExtendableModel
from pdopt.exploration import  ProbabilisticExploration
from pdopt.optimisation import Optimisation
from pdopt.tools import generate_run_report
#from pdopt.visualisation import main_inline

from HE_Model import model, postpro_run


class Experiment(ExtendableModel):
    
    def __init__(self, input_parameters, architecture, mission_file):
        self.inp        = list(pd.read_csv(input_parameters)['name'])
        self.arch       = architecture
        self.arch0      = architecture
        self.mission    = mission_file
        
    def run(self, *args, **kwargs):
        # The input of the model is variable
        # we need to construct the energy management dataframe
        
        X, parms = [], []
        en_mgm = []
        
        # The TO/LND conditions will be single point only
        # logic to convert TO/LND into takeoff, climbout, final, landing
        for i in range(len(self.inp)):

            if 'TO' in self.inp[i]:
                parms.append(self.inp[i].replace('TO','takeoff'))
                parms.append(self.inp[i].replace('TO','climbout'))
                X.append(args[i])
                X.append(args[i])
                
            elif 'LND' in self.inp[i]:
                parms.append(self.inp[i].replace('LND','final'))
                X.append(args[i])
                
            elif 'LNDToAlternate' in self.inp[i]:
                parms.append(self.inp[i].replace('LND','final'))
                parms.append(self.inp[i].replace('LNDToAlternate','landing'))
                X.append(args[i])
                X.append(args[i])
            
            else:
                parms.append(self.inp[i])
                X.append(args[i])
                
        
        # Stuff to introduce constraints over the x_positions
        all_x_vals = []
        x_vals = []
        old_seg = None
        
        for i in range(len(parms)):
            # separate segment from type
            segment, value = parms[i].split('_')
            
            if old_seg != segment and len(x_vals) > 0:
                all_x_vals.append(x_vals)

            x_vals = [] if old_seg != segment else x_vals

            if value[0] == 'h':
                if len(en_mgm) == 0 or en_mgm[-1][0] != segment:
                    en_mgm.append([segment, 0, X[i]])
                else:
                    en_mgm.append([segment, 1, X[i]])
            elif value[0] == 'x':
                x_vals.append(X[i])
                en_mgm[-1][1] = X[i]
                
            old_seg = segment
        all_x_vals.append(x_vals)

        
        en_management = pd.DataFrame(en_mgm, columns=['segment','x','doh'])
        
        #For doing UQ on architecture parameters
        checks = [
            'e_bat' in kwargs.keys(),
            'motor' in kwargs.keys(),
            'power_el' in kwargs.keys(),
            'cables' in kwargs.keys(),
            'battery' in kwargs.keys()
            ]
        
        if any(checks):
            
            if 'e_bat' in kwargs.keys():
                self.arch['e_bat'] = kwargs['e_bat']
                
            if 'motor' in kwargs.keys():
                self.arch['eta_e_comp']['motor'] = kwargs['motor']
                self.arch['eta_e'] = np.prod(
                    list(self.arch['eta_e_comp'].values())
                    )
            
            if 'power_el' in kwargs.keys():
                self.arch['eta_e_comp']['power_el'] = kwargs['power_el']
                self.arch['eta_e'] = np.prod(
                    list(self.arch['eta_e_comp'].values())
                    )
                
            if 'cables' in kwargs.keys():
                self.arch['eta_e_comp']['cables'] = kwargs['cables']
                self.arch['eta_e'] = np.prod(
                    list(self.arch['eta_e_comp'].values())
                    )
        
            if 'battery' in kwargs.keys():
                self.arch['eta_e_comp']['battery'] = kwargs['battery']
                self.arch['eta_e'] = np.prod(
                    list(self.arch['eta_e_comp'].values())
                    )
            
        else:
            self.arch = self.arch0.copy()
        
        
            
        
        
        analysis = model(en_management, architecture_data=self.arch, mission_file=self.mission)
        
        output = {
                'TOM'      : analysis.iloc[-1].mass,
                'Mf'       : analysis.iloc[-1].m_fl,
                'M_NOx'    : analysis.iloc[-1].m_NOx,
                 }
        
        # Add constraints over the position of the segments, x2 - x1 < 0
        if len(all_x_vals) > 0:
            counter = 1
            for x_vals in all_x_vals:
                for i in range(1,len(x_vals)):
                    output.update({f'x{counter}':x_vals[i-1]-x_vals[i]})
                    counter += 1
                
        return output
    
    def postprocess_analysis(self, *args, **kwargs):
        # The input of the model is variable
        # we need to construct the energy management dataframe
        
        X, parms = [], []
        en_mgm = []
        
        # The TO/LND conditions will be single point only
        # logic to convert TO/LND into takeoff, climbout, final, landing
        for i in range(len(self.inp)):
            if 'TO' in self.inp[i]:
                parms.append(self.inp[i].replace('TO','takeoff'))
                parms.append(self.inp[i].replace('TO','climbout'))
                X.append(args[i])
                X.append(args[i])
                
            elif 'LND' in self.inp[i]:
                parms.append(self.inp[i].replace('LND','final'))
                X.append(args[i])
                
            elif 'LNDToAlternate' in self.inp[i]:
                parms.append(self.inp[i].replace('LND','final'))
                parms.append(self.inp[i].replace('LNDToAlternate','landing'))
                X.append(args[i])
                X.append(args[i])
            
            else:
                parms.append(self.inp[i])
                X.append(args[i])
                
        
        for i in range(len(parms)):
            # separate segment from type
            segment, value = parms[i].split('_')
            
            if value[0] == 'h':
                if len(en_mgm) == 0 or en_mgm[-1][0] != segment:
                    en_mgm.append([segment, 0, X[i]])
                else:
                    en_mgm.append([segment, 1, X[i]])
            elif value[0] == 'x':
                en_mgm[-1][1] = X[i]

        
        en_management = pd.DataFrame(en_mgm, columns=['segment','x','doh'])
        
        #For doing UQ on battery energy density
        if 'e_bat' in kwargs.keys():
            self.arch['e_bat'] = kwargs['e_bat']
        else:
            self.arch = self.arch0.copy()
        
        
        analysis = model(en_management, architecture_data=self.arch, mission_file=self.mission)
        
        results = postpro_run(self.arch, analysis)

        return results
    
    
def run_experiment(folder, n_exp_samples, P_exploration, restart, n_exp_train):
    print('Input Args: ', folder, n_exp_samples, P_exploration, restart, n_exp_train)
    
    architecture = json.load(open('data/architecture.json', 'r'))
    mission = 'data/mission_original.csv'
    experiment = Experiment(folder + '/input.csv', architecture, mission)
    
    
    # Check if a design space is already present otherwise create it
    if exists(folder + '/design_space.pk') and restart:
        design_space = pk.load(open(folder + '/design_space.pk','rb'))
    else:
        design_space = DesignSpace(folder + '/input.csv', folder + '/response.csv')
        pk.dump(design_space, open(folder + '/design_space.pk','wb'))
        
    # Check if there is already a trained exploration object
    if exists(folder + '/exploration.pk') and restart:
        exploration = pk.load(open(folder + '/exploration.pk','rb'))
    else:
        exploration = ProbabilisticExploration(design_space, experiment,
                                           surrogate_training_data_file=folder + '/samples.csv',
                                           n_train_points=n_exp_train)
        
        for k in exploration.surrogates:
            s = exploration.surrogates[k]
            print(f'Surrogate {s.name} with r = {s.score:.4f}')
    
        pk.dump(exploration, open(folder + '/exploration.pk','wb'))
    
    
    # Check if exploration has been done already
    if exists(folder + '/exp_results.csv') and restart:
        pass
    else:
        exploration.run(n_exp_samples, P_exploration)
        design_space.get_exploration_results().to_csv(folder + '/exp_results.csv', index=False)
        
        #Update the saved design object
        pk.dump(design_space, open(folder + '/design_space.pk','wb'))
    
    
    optimisation = Optimisation(design_space, experiment, n_max_evals=2000)


    # Check if optimisation has been done already
    if exists(folder + '/opt_results_raw.csv') and restart:
        pass
    else:
        optimisation.run()
        df_opt = design_space.get_optimum_results()
        df_opt.to_csv(folder + '/opt_results_raw.csv', index=False)
        
        #Update the saved design object
        pk.dump(design_space, open(folder + '/design_space.pk','wb'))

    if exists(folder + '/opt_results.csv') and restart:
        pass
    else:
        inp_pars = design_space.par_names #pd.read_csv(inp_files[i])['name'].tolist()
        
        df_opt['M_batt'] = 0
        df_opt['eff']    = 0
        df_opt['M_CO']   = 0
        df_opt['M_CO2']  = 0
        df_opt['eff_GT_cl'] = 0
        df_opt['eff_GT_cr'] = 0
        df_opt['eff_cl'] = 0
        df_opt['eff_cr'] = 0
        
        for index in tqdm(range(len(df_opt))):
            t_out = experiment.postprocess_analysis(*df_opt.loc[index, inp_pars].tolist())
            
            df_opt.loc[index, 'M_batt'] = t_out.iloc[-1].m_bat
            df_opt.loc[index, 'eff'] = t_out.iloc[-1].eff
            df_opt.loc[index, 'M_CO'] = t_out.iloc[-1].m_CO
            df_opt.loc[index, 'M_CO2'] = t_out.iloc[-1].m_fl * 3
            df_opt.loc[index, 'eff_GT_cl'] = t_out.loc[t_out['tag'] == 'climb'].P_GT_out.sum() / t_out.loc[t_out['tag'] == 'climb'].P_GT_in.sum()
            df_opt.loc[index, 'eff_GT_cr'] = t_out.loc[t_out['tag'] == 'cruise'].P_GT_out.sum() / t_out.loc[t_out['tag'] == 'cruise'].P_GT_in.sum()
            df_opt.loc[index, 'eff_cl'] = t_out.loc[t_out['tag'] == 'climb'].P_req.sum() / t_out.loc[t_out['tag'] == 'climb'].P_tot.sum()
            df_opt.loc[index, 'eff_cr'] = t_out.loc[t_out['tag'] == 'cruise'].P_req.sum() / t_out.loc[t_out['tag'] == 'cruise'].P_tot.sum()
            
            t_out.to_csv(folder + f'/missions/{index}_mission_output.csv')
        
        df_opt.to_csv(folder + '/opt_results.csv', index=False)
    
    #Runtime Report
    generate_run_report(folder + '/report.txt', design_space, optimisation, exploration)

if __name__ == '__main__':
    # run experiments with arguments from command line
    parser = argparse.ArgumentParser(description='Run a P-DOPT experiment of the Energy Management Strategy search')
    
    parser.add_argument('folder', 
                        help='Name of the folder where input.csv and response.csv are located')
    
    parser.add_argument('P_sat',  type=float, 
                        help='Minimum total probability for accepting a set/subspace')
    
    parser.add_argument('--restart', action='store_true', 
                        help='Restart from a previously halted run')
    
    parser.add_argument('--n_train',  type=int, default=100,
                        help='N points to train the probabilistic surrogate response')
    
    parser.add_argument('--n_exp',  type=int, default=100,
                        help='N samples to estimate a set/subspace probability')
    
    args = parser.parse_args()

    # if len(sys.argv) > 3 and (sys.argv[3] == 'restart'):
    #     restart=True
    # else:
    #     restart=False
    
    run_experiment(args.folder, args.n_exp, args.P_sat, args.restart, args.n_train)
