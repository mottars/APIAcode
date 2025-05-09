# -*- coding: utf-8 -*-
#%reset
#pip install folium 
#pip install utm
#pip install geopandas

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
import copy

import time
import pandas as pd
import Build_Inspction_Report as BIR

import Generate_Inspection_Map as GIM



# Geolocalização
Plot_Map = 1
plot_seaborn = 1
plot_cluster = 1
planar_plot = 1
longi_plot = 1
time_variable=0
plotson = 1
plot_CGR = 0
plot_match = 0
plot_ispecs = 1
plot_hight = 1
plot_hist = 1
test_Z = 0

# Reliability Analysis
relib_ana=1
Run_compare_ERF_ProbF=0

debugon =  not True
# debugon = False
surce_dir = os.curdir+os.sep+'Files'+os.sep+'Pipeway_SP'

# spreadsheet_namesi = ['PEN-SCA 2006 resumo.csv',
#                     'PEN-SCA 2014 resumo.csv',
#                     'PEN-SCA 2017 resumo.xlsx']

# datesi = [2006, 2014,  2017]

# spreadsheet_names = spreadsheet_namesi[2:3]
# dates = datesi[2:3]

# spreadsheet_names = ['Apendice_F_redz.xlsx']

# Pipeflaw -> simP
# spreadsheet_names = ['I-RL-4710.02-6521-973-RAX-004_R0_F00001-587-02.XLS','Lists.xlsx', 'Apendice_A.xlsx']
# dates = [2010,2017,2023]
spreadsheet_names = ['Apendice_A.xlsx']
# spreadsheet_names = ['Apendice_Aredzd.xlsx']
dates = [2023]

#mm
OD = 14*25.4

XY0 = []

# grid_letter='K'
sige = 323.412
sigu = 442.934
MAOP = 7.97
F = 0.72

# PIG
Insp_type = 'MFL'
Confid_level=0.85
Accuracy=0.1

min_CGR = 0.1
max_CGR = 1.2


n_inp = len(spreadsheet_names)
ij = range(n_inp)
if plot_match:
    # future assessment 
    dt = 5 # years
    
    # Matching between inpections
    ij=[0,1]
else:
    if isinstance(dates,list):
        ij=range(len(dates))
    else:
        dates = [dates]
        ij=[0]

    

# class struct_data:
#         pass

# Inspection = []

#############################################
# Start measuring CPU time
start_time = time.process_time()
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
                         # grid_letter=grid_letter, 
                         sige = sige, sigu = sigu, 
                         MAOP = MAOP, 
                         F = F,
                         Insp_type = typ, 
                         Confid_level=conf, Accuracy=acc)
    Insps.append(Inspi)
    XY0, coln = Insps[i_insp].Tally_read(XY0=XY0, debugon=debugon)
    col_names.append(coln)

print('N of defects\date: ', [[len(i.df_Def), i.date] for i in Insps])
# depth_name, def_len_name , def_w_name,t_name , Y_name , X_name  ,H_name , gridzone_name , tube_num_name , tube_len_name , weld_dist_name , Z_pos_name , circ_pos_name , surf_pos_name , ERF_name , feature_name = col_names

if debugon:
    df_Def = Inspi.df_Def
    print('UTM coordinate: ', df_Def.gridzone.iloc[0], df_Def.gridzone_n.iloc[0], df_Def.gridzone_l.iloc[0], ' X,Y =  ',df_Def.X.iloc[0], df_Def.Y.iloc[0])

##########################################################################
Insps[-1].barlow_eq()

##########################################################################
# Cluster Identification for last inspection
Insps[-1].Identify_Cluster( col_names , debugon = debugon)

##########################################################################
# def insert_cluster_rows()
# save origial single defects index

Insps[-1].df_Def['Single_idx'] = Insps[-1].df_Def.index
df = Insps[-1].df_Def
# cluster_details DF for RBP - FEA, Eff Area (EA) 

cluster_details = pd.DataFrame()
rows = []
for i in range(len(Insps[-1].df_cluster)):
    cluster_i = Insps[-1].df_cluster.iloc[i]
    Zs = np.array([df.Z_pos.loc[cluster_i.defs].values])
    ds = np.array([df.d.loc[cluster_i.defs].values])
    Ls = np.array([df.L.loc[cluster_i.defs].values])
    Ws = np.array([df.W.loc[cluster_i.defs].values])
    ts = np.array([df.t.loc[cluster_i.defs].values])
    idx= Insps[-1].df_cluster['Cluster #'].iloc[i]
    
    add_row = {'id': idx,
               'L': Ls,
               'W': Ws,
               'd': ds,
               'Z': Zs,
               't': ts}
    rows.append(add_row)
    
cluster_details = pd.concat([cluster_details, pd.DataFrame(rows)], ignore_index=True)
cluster_details.index = cluster_details.index+1
df_clstr=[]
for i in range(len(Insps[-1].df_cluster)):
    
    cluster_i = Insps[-1].df_cluster.iloc[i]
    
    # Index of cluster defect 0
    insert_in = cluster_i.defs[0]  # Insert befor this row (index)
    
    # Row to insert
    new_row = df.loc[insert_in:insert_in].copy()
    
    new_row.Z_pos = cluster_i.Z_pos
    new_row.d = cluster_i.d
    new_row.L = cluster_i.L
    new_row.W = cluster_i.W
    new_row['Cluster #'] = cluster_i['Cluster #']
    new_row['Cluster list'] = [cluster_i.defs]
    new_row['Single_idx'] = 0

    new_row.index = [str(insert_in)+'c']
    
    # print('single i', df.loc[insert_in:insert_in])
    # print('clusteri', new_row)
    
    # Split, insert, and concatenate
    
    df_clstr.append(new_row)
    
# # df.sort_index(level=1)
# Insps[-1].df_cluster = pd.concat(df_clstr)
# Insps[-1].df_def = df
Insps[-1].df_Def = pd.concat([Insps[-1].df_Def,pd.concat(df_clstr)])

print('Clusters included in df_Def, new size = ', len(Insps[-1].df_Def ))
##########################################################################



if plot_match:
    ##########################################################################
    # Matching procedure (between "ij" inspection)

    match_Ins0, match_Ins1 = itools.matching(Insps, ij, debugon = debugon)
    print('Defect Matching occurence: ', len(match_Ins1), '/',len(Insps[ij[1]].df_Def))

    ##########################################################################
    # Corrosion Growth Rate calculation (between "ij" inspection)
    CGR, CGRp = itools.CGR_Comput(Insps,ij, match_Ins0, match_Ins1, min_CGR=min_CGR, max_CGR=max_CGR)
    Insps[ij[-1]].add_CGR(CGR, CGRp, min_CGR , max_CGR)

    
    #########################################################################
    ##########################################################################
    # Future Defect sizes  (between "ij" inspection)
    ##########################################################################
    # future data creation
    Insps.append(copy.deepcopy(Insps[ij[-1]]))
    # Dates from inspection used to predict future 
    Dates=[Insps[i].date for i in ij]
    Insps[-1].Future_def(Dates, dt, debugon = debugon)


##########################################################################
# Defects Assessment 
##########################################################################
print('Single defects (Level 1) assessment....')
for i in Insps:
    i.Defects_Analysis(analysis_type = sempiric.modifiedb31g)


##########################################################################
# Cluster Defects Assessment via Effective Area
##########################################################################
print('Cluster defects (Level 2) assessment....')
for i in Insps:
    i.Defects_Analysis(def_type = 'cluster', cluster_details=cluster_details)

############################################################
# Reliability Analysis

if relib_ana==1:
    
    n_Insps = len(Insps)
    for inspi in Insps:
        print('Running Form... ')
        inspi.reliability_analysis()
        print('Number of Form results: ', inspi.df_Def['beta'].count())
        print('Form convergence problems: beta = nan')
        print(inspi.df_Def['beta'].isna().sum())
        print(np.sum(np.isnan(inspi.df_Def['beta'].isna())))
        beta0 = inspi.df_Def['beta'].copy()
        beta0[beta0.isna()]=beta0.max()+1
        plt.figure()
        plt.xscale('log'), plt.plot(inspi.df_Def.PF_form,inspi.df_Def.ERF,marker='.', linewidth=0)
        plt.figure()
        plt.plot(beta0,inspi.df_Def.ERF,marker='.', linewidth=0)
    if Run_compare_ERF_ProbF==1:
        itools.compare_ERF_ProbF(Insps)
############################################################

# User Frendly Data Frame
print('grafical_DF saveing...')
for ii in ij:
    dfg = itools.grafical_DF(Insps[ii])
    Insps[ii].dfg=dfg
    
##############
#Save DF
for i in Insps:
    i.dfg.to_csv('./DataFrames/Defect_Assessment_DF_' + str(i.date) + '.csv')
    i.df_joints.to_csv('./DataFrames/Joints_Inspection_' + str(i.date) + '.csv')   


##############
# MAPs
print('Creating iteractive Map .HTML')
if Plot_Map:
    [m,df_crt] = GIM.plot_map(Insps[-1],'Pipe_Map_PipeWay', d_min=30)


#############################################
# Tables
Insps[-1].ERF_distrib_create()
##############



#############################################
# Printing Critical Defects: ERF>0.92
ERF_lmt = 0.92
crt_test = Insps[-1].critical_def_list(cluster_details,ERF_lmt, plot_cluster=0)
print ('critical def')
crt_test = (Insps[-1].df_Def['ERF']>ERF_lmt)
print ('Level 1= ',Insps[-1].df_Def['ERF'][crt_test])
print ('Level 2= ',Insps[-1].df_Def['ERF_EffArea'][crt_test])


#crt_test = Insps[-1].critical_def_list(cluster_details,ERF_lmt, plot_cluster=1)
crt_details = cluster_details.iloc[Insps[-1].df_Def['Cluster #'][crt_test]-1]

import cluster_EffectArea as cea
for cid in crt_details.id:
    pp,dd=cea.create_intervals(crt_details.loc[cid])
    cea.plot_defects(pp,dd, title = 'Cluster Defect Profile: '+str(cid))
    
#############################################


##############
# PLOTS ###
   

if plot_seaborn:
    # plot_seaborns(Inspection,  col_names,ij =[0,1], XY0=[], min_joint_dist = 0.5):
    itools.plot_seaborns(Insps, col_names,ij,plot_match, planar_plot = planar_plot, longi_plot = longi_plot )
    
    if relib_ana==1:
        itools.plot_seab_prob(Insps, col_names,ij, planar_plot = planar_plot, longi_plot = longi_plot )
        


if plot_cluster:
    # plot_seaborns(Inspection,  col_names,ij =[0,1], XY0=[], min_joint_dist = 0.5):
    itools.plot_cluster(Insps[-1].cluster_list())
    
###############################################
### REFORMATING -> PAREI AQUI
###############################################

# PI.X


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
        plt.savefig('Depth_histogram.png', dpi=400)
        
        plt.figure()
        plt.hist(Insps[0].df_Def.ERF,bins=40)
        plt.title('ERF Distribution')
        plt.xlabel('ERF')
        plt.ylabel('frequence')
        plt.savefig('ERF_histogram.png', dpi=400)
    
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
        plt.savefig('Features_position.png', dpi=400)
    
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
        plt.savefig('Metal_Loss_position.png', dpi=400)
        
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
        plt.savefig('Match_position.png', dpi=400)
        
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
        plt.savefig('CGR.png', dpi=400)
    
BIR.Criar_Relatorio(file_name = f'Relatorio_de_Inspecao{dates[-1]}.docx', insp=Insps[-1])

# End measuring CPU time
end_time = time.process_time()
cpu_time = end_time - start_time

print(f"CPU time taken: {cpu_time:.2f} seconds")

######################################################
# import pickle as pk
# with open('Inspection_file.pickle', 'wb') as f:
#     pk.dump(Insps, f)
######################################################
# import pickle as pk
# with open('Inspection_file.pickle', 'rb') as f:
#     Insps = pk.load(f)
######################################################