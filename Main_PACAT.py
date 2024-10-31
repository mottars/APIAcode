# -*- coding: utf-8 -*-
#%reset

import inspection_tools as itools
# from inspection_tools import get_spreadsheet_labels, pre_proc_df, inspection_match, CGR_Comput, find_clusters
# from inspection_tools import   CGR_Comput, plot_seaborns, compare_ERF_ProbF, matching, comput_MSOP, def_critical_limits
import Pipe_Inspection as PI
# import pandas as pd
import os
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

from python_scripts import main_pipe_normas as sempiric

# import Sistema_Cordut.Risk_Module as risk
# from python_scripts import main_pipe_normas as sempiric
# import Sistema_Cordut.main_pipe_normas as semi_empiric

# import sys
# import seaborn as sns
# import itertools
# import matplotlib as mpl
# import python_scripts.main_pipe_normas as normas


relib_ana = 1

Plot_Map = 1
plot_seaborn = 1
time_variable=0
plotson = 1
plot_CGR = 0
plot_match = 1
plot_ispecs = 1
plot_hight = 1
plot_hist = 1
test_Z = 0


surce_dir = os.curdir+os.sep+'Files'

spreadsheet_names = ['PEN-SCA 2006 resumo.csv',
                    'PEN-SCA 2014 resumo.csv',
                    'PEN-SCA 2017 resumo.xlsx']
dates = [2006, 2014,  2017]


OD = 32*25.4

grid_letter='J'
sige = 485
sigu = 565 
MAOP = 10 
Insp_type = 'MFL'
Confid_level=0.85
Accuracy=0.1


min_CGR = 0.1
max_CGR = 1.2

# future assessment 
dt = 5 # years

# Matching between inpections
ij=[0,1]
debugon = False
XY0 = []

# class struct_data:
#         pass

# Inspection = []

#############################################
#Inspection read!!
col_names=[]
Insps = []
n_inp = len(spreadsheet_names)
for i_insp in range(n_inp):
    if np.size(Accuracy)==1:
        acc=Accuracy;conf=Confid_level;typ=Insp_type
    else:
        acc=Accuracy[i_insp];conf=Confid_level[i_insp];typ=Insp_type[i_insp]
            
    #def __init__(self, file_name, date, OD, surce_dir='',future=False, grid_letter='J', sige = 485, sigu = 565, MAOP = 10, Insp_type = 'MFL',Confid_level=0.85, Accuracy=0.1, acc_rel = 0.05):
    Inspi = PI.Inspection_data(spreadsheet_names[i_insp], dates[i_insp], OD, surce_dir, 
                         grid_letter=grid_letter, 
                         sige = sige, sigu = sigu, 
                         MAOP = MAOP, 
                         Insp_type = typ, 
                         Confid_level=conf, Accuracy=acc)
    Insps.append(Inspi)
    XY0, coln = Insps[i_insp].Tally_read(XY0=XY0, debugon=debugon)
    col_names.append(coln)

print('N of defects\date: ', [[len(i.df_Def), i.date] for i in Insps])
# depth_name, def_len_name , def_w_name,t_name , Y_name , X_name  ,H_name , gridzone_name , tube_num_name , tube_len_name , weld_dist_name , Z_pos_name , circ_pos_name , surf_pos_name , ERF_name , feature_name = col_names
df_Def = Inspi.df_Def
if debugon: print('UTM coordinate: ', df_Def.gridzone_name.iloc[0], ' S ',df_Def.X_name.iloc[0], df_Def.Y_name.iloc[0])


##########################################################################
# Matching procedure (between "ij" inspection)
match_Ins0, match_Ins1 = itools.matching(Insps, ij, debugon = False)
print('Defect Matching occurence: ', len(match_Ins1), '/',len(Insps[ij[1]].df_Def))

##########################################################################
# Corrosion Growth Rate calculation (between "ij" inspection)
CGR, CGRp = itools.CGR_Comput(Insps,ij, match_Ins0, match_Ins1, min_CGR=min_CGR, max_CGR=max_CGR)
Insps[ij[-1]].add_CGR(CGR, CGRp, min_CGR , max_CGR)

##########################################################################
# Cluster Identification for last inspection
Insps[-1].Identify_Cluster( col_names , debugon = False)


#########################################################################
##########################################################################
# Future Defect sizes  (between "ij" inspection)
##########################################################################
import copy
# future data creation
Insps.append(copy.deepcopy(Insps[ij[-1]]))
# Dates from inspection used to predict future 
Dates=[Insps[i].date for i in ij]
Insps[-1].Future_def(Dates, dt, debugon = debugon)



##########################################################################
# Defects Assessment 
##########################################################################
for i in Insps:
    i.Defects_Analysis(analysis_type = sempiric.modifiedb31g)


###################################
# Printing Critical Defects: ERF>0.99
print_critical = 0
if print_critical:
    MSOP = Insps[-1].df_Def['MSOP']
    print('Critical Defects: ERF>0.99')
    id_crit = np.where(MAOP/MSOP>0.99)
    for i in id_crit[0]:
        print(Insps[-1].df_Def.iloc[i])
        
#############################################
##############
#Save DF
for i in Insps:
    i.df_Def.to_csv('./DataFrames/Defect_Assessment_' + str(i.date) + '.csv')
    i.df_joints.to_csv('./DataFrames/Joints_Inspection_' + str(i.date) + '.csv')   

##############
##############
# MAPs
if Plot_Map:
    Insps[-1].plot_map('Pipe_Map_novo',ERF_min=0.9, d_min=15)

############################################################
# Reliability Analysis
relib_ana=0
if relib_ana==1:
    
    n_Insps = len(Insps)
    for inspi in Insps:
        inspi.reliability_analysis()
        print('Form convergence problems?:')
        print(np.sum(np.isnan(inspi.df_Def['beta'])))

    itools.compare_ERF_ProbF(Insps)
############################################################
# PLOTS ###

###############################################
### REFORMATING -> PAREI AQUI
###############################################

# PI.X

if plot_seaborn:
    # plot_seaborns(Inspection,  col_names,ij =[0,1], XY0=[], min_joint_dist = 0.5):
    itools.plot_seaborns(Insps, col_names,ij)
    # print ("end")

if time_variable:
    ############################################################
    # Time dependent ERF
    df=Insps[-1].df_Def
    # Meters
    D  = Insps[-1].OD/1000
    L  = df.L.values/1000
    t  = df.t.values/1000
    dp = df.d.values/100 # dp(%)
    T = 10 #anos
    dp0 = df_Def.d.values/100
    dts = np.linspace(0,T,T*4+1)
    nts = len(dts)
    ndef = len(dp0)
    
    ERFs = np.zeros([ndef,nts])
    Nfail = np.zeros(nts)
    plt.figure()
    for i in range(len(dts)):
        dp = dp0 + dts[i]*CGRp
        MSOPbar = itools.comput_MSOP(D,t,dp,L,sige,sigu)
        ERFi = MAOP/MSOPbar
        ERFs[:,i] =  ERFi
        Nfail[i] = sum(ERFi>0.99)
    
    plt.figure()
    plt.plot(dts,ERFs.transpose())
    plt.plot([0,T],[1,1])
    plt.ylim(0.9,1.05)
    plt.xlabel('Time Interval (y)')
    plt.ylabel('EFR')
    
    plt.figure()
    plt.bar(dts,Nfail)
    plt.xlabel('Time Interval (y)')
    plt.ylabel('Number of critical points (ERF>ERF_crit)')


if plotson:    
    
    #############################################
    #############################################
    #############################################
    # PLOTS
    #############################################
    #tubes positioning
    X0 = XY0[0]
    Y0 = XY0[1]
    Z0 = XY0[2]
    if test_Z:
        tube_X = list(Insps[0].df_joints.X)
        tube_Y = list(Insps[0].df_joints.Y)
        n_tubes = len(Insps[0].i_joints)
        # Comput Real_Z
        tube_len = np.zeros(n_tubes)
        for i in range(n_tubes-1):
            dx = tube_X[i+1]-tube_X[i]
            dy = tube_Y[i+1]-tube_Y[i]
            tube_len[i] = (dx**2+dy**2)**.5
        
        # Testing odometer
        Z_tube = list(Insps[0].df_joints.Z)
        tube_lenZ = np.zeros(n_tubes)
        for i in range(n_tubes-1):
            tube_lenZ[i] = Z_tube[i+1]-Z_tube[i]
            
        # Not in spreadsheet
        tube_len[-1] = Insps[0].df_joints.tube_len.iloc[-1]
        tube_lenZ[-1]= Insps[0].df_joints.tube_len.iloc[-1]
        S_pos = np.cumsum(tube_len)
        Insps[0].i_joints.pop(n_tubes-1)
        n_tubes = len(Insps[0].i_joints)
        if debugon: print('n_Tubes: ',n_tubes)
        if debugon: print('Tubes: ',len(tube_len))
        # for i in i_joints:
        #     if not np.isnan(df[tube_num_name][i]):
        #         i_joints.append(i)
        
        
        plt.figure()
        plt.plot(S_pos,Insps[0].df_joints.tube_len-tube_lenZ,'x',c='k')
        plt.plot(S_pos,tube_len-tube_lenZ,'+',c='r')
        plt.plot(S_pos,tube_lenZ-tube_lenZ,'.', c='b')
        
        plt.title(['tubes length dif GPSxZ',Insps[0].file_name])
        plt.xlabel('S dist')
        plt.ylabel('diff')
    #############################################
    
    if plot_hist:
        plt.figure()
        plt.hist(Insps[0].df_Def.d,bins=40)
        plt.title('Depth Distribution')
        plt.xlabel('depth')
        plt.ylabel('frequence')
    
    if plot_hight:
        df = Insps[0].df_Def
        plt.figure()
        ax = plt.subplot()
        im = plt.scatter(df.X , df.Y,marker='.',c=df.H)
        plt.title(['Features position ',Insps[0].file_name])
        plt.xlabel('Easting')
        plt.ylabel('Norting')
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax)
    
    if plot_ispecs:
        markers = ['o','+', 'x', '>', '.', 's']
        fig=plt.figure()
        ax = plt.subplot()
        X = Insps[0].df_joints.X
        Y = Insps[0].df_joints.Y
        plt.plot(X, Y)
        n_Insps = len(Insps)
        for i in range(n_Insps):
            print(Insps[i].file_name)
            X = Insps[i].df_Def.X 
            Y = Insps[i].df_Def.Y 
            Z = Insps[i].df_Def.d
            label = Insps[i].file_name
            im = plt.scatter(X, Y,marker=markers[i],c=Z, s=(n_Insps-i)*60, label=label)
        plt.legend()
        plt.title(['Metal Loss position '])
        plt.xlabel('Easting')
        plt.ylabel('Norting')
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax)
    #plt.figure()
    
    ##########################################################
    # plot_match
    if plot_match:
        markers = ['o','+', 'x', '>', '.', 's']
        fig=plt.figure()
        ax = plt.subplot()
        X = Insps[0].df_joints.X 
        Y = Insps[0].df_joints.Y 
        plt.plot(X, Y)
        for i in range(n_Insps-1):
            print(Insps[i].file_name)
            ####################### 
            # Insps 0
            X = Insps[i].df_Def.X.iloc[match_Ins0] 
            Y = Insps[i].df_Def.Y.iloc[match_Ins0] 
            label = Insps[i].file_name
            plt.scatter(X, Y,marker=markers[i],edgecolors='r', facecolors='none', s=80, label=label)
            
            ####################### 
            # Insps 1
            X = Insps[i+1].df_Def.X.iloc[match_Ins1] 
            Y = Insps[i+1].df_Def.Y.iloc[match_Ins1] 
            label = Insps[i+1].file_name
            plt.plot(X, Y,marker=markers[i+1], linewidth=0, label=label, color='k')
            
            ####################### 
            
        plt.legend()
        plt.title(['Match position '])
        plt.xlabel('Easting')
        plt.ylabel('Norting')
        
        # divider = make_axes_locatable(ax)
        # cax = divider.append_axes("right", size="5%", pad=0.05)
        # plt.colorbar(im, cax=cax)  
      
    
    if plot_CGR:
        markers = ['o','+', 'x', '>', '.', 's']
        fig=plt.figure()
        ax = plt.subplot()
        X = Insps[0].df_joints.X - X0
        Y = Insps[0].df_joints.Y - Y0
        plt.plot(X, Y)
        for i in range(n_Insps-1):        
            X = Insps[i+1].df_Def.X - X0
            Y = Insps[i+1].df_Def.Y - Y0
            im = plt.scatter(X, Y, c = CGR, s=50, label='CGR', facecolors='none',marker='o' )
            
            ####################### 
            
        plt.legend()
        plt.title(['CGR '])
        plt.xlabel('Easting')
        plt.ylabel('Norting')
        
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax)  
    