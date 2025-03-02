# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 11:33:12 2022

@author: MottaRS
"""

import numpy as np
import pandas as pd
import datetime as datt
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.cm as mcm
import cluster_EffectArea as cea

##################################################
import seaborn as sns
# import matplotlib.cm as mcm

#############################################
# Match between joint position using LCRS algorithm
# Monotonic_Real_Sequences_Intersection
from Algorithms import MRSI_3D
from python_scripts import main_pipe_normas as sempiric

debugon = False

def skp_header(df, debugon = False):
    if any (df.columns.str.contains('^Unnamed:')):

        max_columns =len(df.columns.values)
        if debugon: print("N Columns = ",max_columns)
        
        for ind, row in df.iterrows():
            if row.count() == max_columns:
                strt_row=ind
                if debugon: print("Start_row = ",ind)
                break
        df.columns = df.iloc[strt_row]
        if debugon: print("Columns = ",df.columns)
    
        # Drop rows above the start_row
        df = df.iloc[strt_row + 1:].reset_index(drop=True)
    return df

def get_spreadsheet_labels(Labels, debugon = False):
    
    #################################################
    # Procurar labels pre-determinados?????????
    ## select columns by regular expression
    ## df.filter(regex='e$', axis=1)
    # print("find")
    # length_cols = ['$len$[mm]$', 'Len']
    # Labels.filter(regex=length_cols, axis=1)
    # for lab_i in Labels :
    #     print(lab_i)
        
    #     if lab_i in length_cols: print(lab_i+'<---'); d_col = lab_i; 
    #################################################
    
    #################################################
    # Find those automatically ???
    
    if debugon: print("Columns = ",Labels)
    if debugon: print("Columns type = ",Labels[0])
    if Labels[0].lower() == 'log dist. [m]'.lower():
        # 2006
        depth_col = 'depth [%]'
        def_len_col = 'length [mm]'
        def_w_col = 'width [mm]'
        t_col = 't [mm]'
        
        #Georeferencing
        Y_col = 'northing [m]'
        X_col = 'easting [m]'
        H_col = 'heighting [m]'
        gridzone_col = 'gridzone'
        
        #Pipe position
        tube_num_col = 'J. no.'
        tube_len_col = 'J. len [m]'
        weld_dist_col = 'to u/s w. [m]'
        Z_pos_col = 'log dist. [m]'
        circ_pos_col = 'o\'clock'
        surf_pos_col = 'internal'
        
        #Others
        ERF_col = 'ERF'
        feature_col = 'event / comment'
        Corrosion_comment = ['metal loss']
        
    elif Labels[0].lower() == 'log distance [m]'.lower():
        # 2014
        #'log distance [m]', 'gridzone', 'easting [m]','northing [m]','height [m]','event / comment','J. no.','J. len [m]','t [mm]','to u/s w. [m]','o\'clock','depth [%]','ERF','length [mm]','width [mm]','internal
        depth_col = 'depth [%]'
        def_len_col = 'length [mm]'
        def_w_col = 'width [mm]'
        t_col = 't [mm]'
        
        #Georeferencing
        Y_col = 'northing [m]'
        X_col = 'easting [m]'
        H_col = 'height [m]'
        gridzone_col = 'gridzone'
        
        #Pipe position
        tube_num_col = 'J. no.'
        tube_len_col = 'J. len [m]'
        weld_dist_col = 'to u/s w. [m]'
        Z_pos_col = 'log distance [m]'
        circ_pos_col = 'o\'clock'
        surf_pos_col = 'internal'
        
        #Others
        ERF_col = 'ERF'
        feature_col = 'event / comment'
        Corrosion_comment = [
            'MELO-CORR  / note 1, PR# 01',
            'MELO-CORR  / note 1, PR# 02',
            'MELO-CORR  / PR# 03',
            'MELO-CORR  / PR# 04',
            'MELO-CORR  / PR# 05',
            'MELO-CORR  / PR# 06',
            'MELO-CORR  / PR# 07',
            'MELO-CORR  / PR# 08',
            'MELO-CORR  / PR# 09',
            'MELO-CORR  / PR# 10',
            'MELO-CORR  / PR# 12',
            'MELO-CORR  / PR# 13',
            'MELO-CORR  / PR# 14',
            'MELO-CORR  / PR# 15',
            'MELO-CORR  / PR# 16',
            'MELO-CORR  / PR# 17',
            'MELO-CORR']

        
    elif Labels[0].lower() == '#':
        # 2017
        #'#' 'Joint number' 'Pipe length, m' 'Relative distance, m'
 # 'Absolute distance, m' 'Comments' 'Depth, %WT/OD' 'Length, mm'
 # 'Width, mm' 'WT, mm' 'Orientation, hrs : mins' 'Wall side'
 # 'ERF (B31G and BS 7910)' 'Easting, m' 'Northing, m' 'Height, m'
        depth_col = 'Depth, %WT/OD'
        def_len_col = 'Length, mm'
        def_w_col = 'Width, mm'
        t_col = 'WT, mm'
        
        #Georeferencing
        Y_col = 'Northing, m'
        X_col = 'Easting, m'
        H_col = 'Height, m'
        gridzone_col = 'gridzone'
        
        #Pipe position
        tube_num_col = 'Joint number'
        tube_len_col = 'Pipe length, m'
        weld_dist_col = 'Relative distance, m'
        Z_pos_col = 'Absolute distance, m'
        circ_pos_col = 'Orientation, hrs : mins'
        surf_pos_col = 'Wall side'
        
        #Others
        ERF_col = 'ERF (B31G and BS 7910)'
        feature_col = 'Comments'
        Corrosion_comment = ['metal loss', 'metal loss (grouped)']
        
    
    elif Labels[0].lower() == 'ID Junta\nAnterior'.lower():
        # New Pipeway
        depth_col = 'Prof.\n(%)'
        def_len_col = 'Compr.\n(mm)'
        def_w_col = 'Larg.\n(mm)'
        t_col = 'Esp.\n(mm)'
        
        #Georeferencing
        Y_col = 'Northing\n(m)'
        X_col = 'Easting\n(m)'
        H_col = 'Height\n(m)'
        gridzone_col = 'Zone'
        
        #Pipe position
        tube_num_col = 'ID Junta\nAnterior'
        tube_len_col = 'Compr.\nTubo\n(m)'
        weld_dist_col = 'Dist. Sld.\nAnt.\n(m)'
        Z_pos_col = 'Posição\n(m)'
        circ_pos_col = 'Posição\nHorária\n(hh:mm)'
        surf_pos_col = 'I/E'
        
        #Others
        ERF_col = 'ERF'
        feature_col = 'Descrição'
        Corrosion_comment = ['CORR']
        
    else:
        print('set columns', Labels)
        print('in def get_spreadsheet_labels(Labels):')
    #################################################
    
    col_names  = [depth_col, def_len_col , def_w_col,t_col , X_col  , Y_col , H_col , gridzone_col , tube_num_col , tube_len_col , weld_dist_col , Z_pos_col , circ_pos_col , surf_pos_col , ERF_col , feature_col ]
    # print(Corrosion_comment)
    return col_names , Corrosion_comment

def time_to_rad(times):
    # Circunferencial position
    # ndata = len(time)
    
    sec360 = 43200*2 #12*60*60 *2 (24)
    
    try:
        # Pandas.to_datetime data type
        secnds_i = times.dt.hour*3600 + times.dt.minute*60 + times.dt.second
    except:
        # datetime.time data type
        secnds_i = times.apply(lambda x: x.hour*3600 + x.minute*60 + x.second) 
        
    rad = secnds_i/sec360
    
    return rad

def plot_clusters(cluster_details,id_cluster):
    
    Ls = cluster_details.loc[id_cluster].L
    ts = cluster_details.loc[id_cluster].t
    ds = cluster_details.loc[id_cluster].d
    Zs = cluster_details.loc[id_cluster].Z*1000
    Zs = Zs - (np.min(Zs) - np.max(Ls))
    x0 = Zs - Ls/2
    x1 = Zs + Ls/2
    y0 = ts*(1 - ds/100)
    y1 = ts
    plt.figure()
    for k in range(len(Ls)):
        plt.plot([x0[k],x1[k],x1[k],x0[k],x0[k]],[y0[k],y0[k],y1[k],y1[k],y0[k]])
    plt.xlabel('long. dist. (mm)')
    plt.ylabel('Wall tickness (mm)')
    plt.title('Cluster Defect ID:'+ str(id_cluster))

def pre_proc_df(df,col_names, Corrosion_comment,XY0=[], debug_on = False):
    
    # 1 - Rename columns name for predifined ones
    # 2 - Filing blank spaces (NaN): tube number, thicks, tube_len.
    #  2.1-Create S position (absolut length)
    # 3 - Filtering ML (Metal Loss) data frame
    #  3.1- Convert oclock position in degree
    #  3.2- Filter predefined Corrosion Comments Only!
    #################################################
      
    #################################################
    # 1 - Rename Columns    
    # Standard Names
    standard_col_names = ['d', 'L', 'W', 't', 'X', 'Y', 'H', 'gridzone', 'tube_num', 'tube_len', 'ref_dist', 'Z_pos', 'clock_pos', 'surf_pos', 'ERF', 'feature']
    for i in range(len(col_names)):
        df=df.rename(columns={col_names[i]: standard_col_names[i]})
    
    col_names = standard_col_names
    depth_col, def_len_col , def_w_col,t_col , X_col  ,Y_col , H_col , gridzone_col , tube_num_col , tube_len_col , weld_dist_col , Z_pos_col , circ_pos_col , surf_pos_col , ERF_col , feature_col = col_names 
    
    
    # Nao lembro pra q!!!!!!!!!!!
    numerical_cols = ['d', 'L', 'W', 't', 'X', 'Y', 'H', 'tube_num', 'tube_len', 'ref_dist', 'Z_pos', 'ERF']
    df[numerical_cols] = df[numerical_cols].apply(pd.to_numeric, errors='coerce')
    
    df = df.dropna(subset='X')
    
    # Gambiarra!!!!!
    if not gridzone_col in df.columns:
        df[gridzone_col]=22
        
    # print('df Filtrate = ')
    # print(df[col_names])
    
    
    #################################################
    # Create S position (absolut in-line length) xxxxxxxxxxxx
    # Filing blank spaces (with NaN): tube number, thicks, tube_len.
    #################################################
    #Add real positions S
    n_df = len(df)
    
    if len(XY0)==0: XY0 = [df.X.iloc[0],df.Y.iloc[0], df.H.iloc[0]]
    
    X = list(df.X)
    Y = list(df.Y)
    Z = list(df.H)
    
    ###########################################################
    # Computing S position
    section_len = np.zeros(n_df)
    current_tub_num = 0
    current_tub_len = 0
    current_t = 0
    joint_pos=[]
    section_len[0] = ((X[0]-XY0[0])**2+(Y[0]-XY0[1])**2+(Z[0]-XY0[2])**2)**.5
    current_tube_num = 0
    # j0=0
    for i in range(n_df-1):
        j=df.index[i]
        dx = X[i+1]-X[i]
        dy = Y[i+1]-Y[i]
        dz = Z[i+1]-Z[i]
        section_len[i+1] = (dx**2+dy**2+dz**2)**.5
        if i>1:
            
            # Copy tube number and length if it's empty
            # if np.isnan(df.tube_len[j]):
            #     df.loc[j,tube_num_col] = df.tube_num[j0]
            #     df.loc[j,tube_len_col] = df.tube_len[j0]
            if df.tube_num[j] != current_tube_num:
                if ~np.isnan(pd.to_numeric(df.tube_num[j])):
                    current_tube_num = df.tube_num[j]
                    joint_pos.append(j)
                    # j0 = j
            
        
        # Filling tube number
        if ~np.isnan(df.tube_len[j]):
            # joint_pos.append(j)
            current_tub_num = df.tube_num[j]
            current_tub_len = df.tube_len[j]
            # if np.isnan(current_tub_len):
            #     print(i)
            #     print(current_tub_num)
            #     print(current_tub_len)
            
        else:
            df.loc[j,tube_num_col] = current_tub_num
            df.loc[j,tube_len_col] = current_tub_len
            # print(idx)
            # print(current_tub_len)

        # Filling Thicks
        if ~np.isnan(df[t_col][j]):
            current_t = df[t_col][j]
            
        else:
            df.loc[j,t_col] = current_t
        
        
    S_pos = np.cumsum(section_len) #+ df['Z_pos'][0]
    df['S_pos']=S_pos
    ##############################
    ###########################################################

    ###########################################################
    ## Filtering ML (Metal Loss) data frame
    
    df.d = pd.to_numeric(df.d, errors='coerce')
    df_Def = df.dropna(subset='d')
    
    # df_Def=df.drop(df[np.isnan(df.d)].index)
    
    # if debug_on:
    plt.figure()
    features_count=Counter(df_Def[feature_col])
    # print(features_count)
    plt.barh(list(features_count),list(features_count.values()))
    # Namimg the x and y axis
    plt.xlabel('Number of features')
    plt.ylabel('ML Comments')
    # Giving the tilte for the plot
    # Inspection[-1].file_col
    plt.title('Features with ML (depth) data')
    plt.savefig('anomalies_histogram.png', dpi=300, bbox_inches='tight')
    # plt.figure()
    # plt.hist(df_Def[feature_col])
    
    
    ########## Filter predefined Corrosion Only!
    #df_Def['is_corrosion'] = df_Def[feature_col].apply(lambda x: x==Corrosion_comment[0])
    
    criterion = df_Def[feature_col].map(lambda x: any(small_str in x for small_str in Corrosion_comment)) 
    df_Def=df_Def[criterion]
    ###########################################################

    
    #################################################
    # Convert oclock position in degree
    # plt.figure()
    # aa= [int(str(il)[0:1]) for il in df[df[circ_pos_col].notnull()][circ_pos_col]]
    # plt.hist(aa)
    # plt.figure()
    # features_count=Counter(aa)
    # # print(features_count)
    # plt.barh(list(features_count),list(features_count.values()))
    
    # print(df_Def[circ_pos_col].iloc[0])
    # i_nnan=df_Def[circ_pos_col].notna().idxmax()
    # print(df_Def[circ_pos_col].loc[i_nnan])
    # print(i_nnan)
    # print(type(df_Def[circ_pos_col].loc[i_nnan]))
    if isinstance(df_Def[circ_pos_col].iloc[0], datt.time):
        print('in time: ', df_Def[circ_pos_col].iloc[0])
        rad = time_to_rad(df_Def[circ_pos_col])
        
    elif isinstance(df_Def[circ_pos_col].iloc[0], str):
        print('in str: ', df_Def[circ_pos_col].iloc[0])
        a = df_Def[circ_pos_col]
        circ_pos = pd.to_datetime(a, format='mixed')
        rad = time_to_rad(circ_pos)
    df_Def[circ_pos_col] = rad
    #################################################
    
    # df_Def=df_Def[[df_Def[feature_col]==Corrosion_comment].index]
    

    #################################################
    ## Filtering joints (tubes) data frame by [tube length]
    #################################################
    #df_joints=df.drop(df[np.isnan(df.tube_len)].index)
    df_joints = df.loc[joint_pos]

    joint_items = ['S_pos', Y_col , X_col  ,H_col , gridzone_col, t_col, tube_num_col , tube_len_col , Z_pos_col , feature_col ]
    df_joints=df_joints.filter(items=joint_items)
    
    
    # df.d = pd.to_numeric(df.d, errors='coerce')
    
    i_joints = list(df[(~np.isnan(df.tube_num))].index)
    if debugon: print('colums: ', df_joints.columns.values)    
    
    i_def = list(df[(~np.isnan(df.d))].index)
    if debugon: print('def cases: ',len(i_def))
    if debugon: print('len(df_joint): ',len(df_joints))
    
    
    # select_col = df[depth_col,def_len_col, def_w_col, t_col, ]
    # print("SINTETIC VALUES d*1, L*1.")

    return df_Def, i_def, df_joints, i_joints, col_names, df, XY0
    

def matching(Insps, ij=[0,1], debugon = False):


    #############################################
    ########### MATCHING PROCESS ################
    #############################################
    #############################################
    print('# Joints Geopositioning Match Analysis... ')
    pp, poss = joints_match(Insps, ij, debugon= debugon)
    
    # Add Joint Match Column
    for i in [0,1]:
        Insps[ij[i]].df_joints['Match'] =pp[i]
        Insps[ij[i]].joint_math = poss
    
    #############################################
    print('# Defect matchin process...')
    match_Ins0, match_Ins1 = defects_match(Insps, ij,tol = 0.1, debugon= debugon)
    
    return match_Ins0, match_Ins1
    

def joints_match(Inspection, ij=[0,1], XY0=[], tol = 50, debugon=False):
    
    # depth_col, def_len_col , def_w_col,t_col , Y_col , X_col  ,H_col , gridzone_col , tube_num_col , tube_len_col , weld_dist_col , Z_pos_col , circ_pos_col , surf_pos_col , ERF_col , feature_col = col_names 
    
    i0=ij[0]
    i1=ij[1]
    
    if len(XY0)==0: XY0 = [Inspection[i0].df_joints.X.iloc[0],
                           Inspection[i0].df_joints.Y.iloc[0],
                           Inspection[i0].df_joints.H.iloc[0]]
    
    X0 = XY0[0]
    Y0 = XY0[1]
    Z0 = XY0[2]

    x0=Inspection[i0].df_joints.X.values - X0
    y0=Inspection[i0].df_joints.Y.values - Y0
    z0=Inspection[i0].df_joints.H.values - Z0
    # S0 = np.asarray((x0**2 + y0**2)**.5)
    
    x1=Inspection[i1].df_joints.X.values - X0
    y1=Inspection[i1].df_joints.Y.values - Y0
    z1=Inspection[i1].df_joints.H.values - Z0
    # S1 = np.asarray((x1**2 + y1**2)**.5)
    
    # S0=Inspection[0].df_joints['S_pos'].values
    # S1=Inspection[1].df_joints['S_pos'].values
    
    # a,p=LCRS_linear(S0,S1,tol)
    # p, p0, p1 = MRSI(S0, S1,tol)
    
    A=np.array([[x0[i],y0[i],z0[i]] for i in range(len(x0)) ])
    B=np.array([[x1[i],y1[i],z1[i]] for i in range(len(x1)) ])
    
    #Monotonic_Real_Sequence_Intersection
    print('Monotonic_Real_Sequence_Intersection Algorithm for joints matching in progress...')
    p, p0, p1 = MRSI_3D(A, B,tol)
    print('MRSI finished ')    
    
    # P0 = [il[0] for il in posa]
    # P1 = [il[1] for il in posa]
    
    pp=[p0,p1]
    
    
    if debugon:
        # Mean intersect position
        Ae = np.array([[x0[il[0]],y0[il[0]],z0[il[0]]] for il in p])
        Be = np.array([[x1[il[1]],y1[il[1]],z1[il[1]]] for il in p])
        
        diff_match = Ae-Be
        n0,n1 = len(A),len(B)
        n_j_match = len(p)
        
        print('Match of inspections: ', ij)
        print('Joints Match occourence: ', n_j_match, '/',min(n0,n1))
        print('Joints Match Bias (X,Y,Z): ', np.mean(diff_match,axis=0))
        print('Mean Joints Match Error (X,Y,Z): ', np.mean(abs(diff_match),axis=0))
    
    return pp, p
    
def defects_match(Inspection, ij=[0,1], XY0=[], tol = 0.1, debugon=False):
    #Match beetwen 2 inspections (0 and 1) 
    
    # depth_col, def_len_col , def_w_col,t_col , Y_col , X_col  ,H_col , gridzone_col , tube_num_col , tube_len_col , weld_dist_col , Z_pos_col , circ_pos_col , surf_pos_col , ERF_col , feature_col = col_names 
    # Match Tolerance 
    # tol
    i0=ij[0]
    if len(XY0)==0: XY0 = [Inspection[i0].df_joints.X.iloc[0],
                           Inspection[i0].df_joints.Y.iloc[0],
                           Inspection[i0].df_joints.H.iloc[0]]
    
    
    # n_inspection = len(ij)
    emptint = -1
    # match[:] = np.nan
    for i in ij[0:-1]:
        match = np.zeros(len(Inspection[i].df_Def),int) + emptint 
        match1= np.zeros(len(Inspection[i+1].df_Def),int) + emptint 
        
        # S0 = Inspection[i].df_Def['S_pos']
        # d0 = Inspection[i].df_Def.d
        
        
        ##################
        # Posicao das juntas anteriores de cada defeito
        tub_def = Inspection[i].df_Def.tube_num
        n0 = len(tub_def)
        if debugon: print("N tub_def: ", n0)
        
        #loop on the defects
        for j in range(n0):
            
            if debugon: print("N: ", j)
            # Distance def to joint 0
            J0 = tub_def.iloc[j]
            Zdef0 = Inspection[i].df_Def.Z_pos.iloc[j]
            
            # find joint of def j
            jointi0 = Inspection[i].df_joints.loc[Inspection[i].df_joints.tube_num==J0]
            
            Zj0 = jointi0.Z_pos.values
            dZ0 = Zdef0 - Zj0
            # dr = ( (X_j0 - Xj1)**2 + (Y_j0 - Yj1)**2 + (Z_j0 - Zj1)**2 )**0.5
            # join_in_df1 = np.argmin(dr)
            
            # Matching joint value
            mj0=jointi0['Match'].values
            if mj0[0]==0:
                if debugon: print( 'mj0[0]==0 ?????????', mj0)
                
            if mj0[0]==-1:
                if debugon: print( 'mj0[0]==-1 ?????????, J0: ', mj0, J0)

            # Find joint in 2nd Inspection
            join_in_df1 = Inspection[i+1].df_joints.loc[Inspection[i+1].df_joints['Match']==mj0[0]]
            
            if debugon: print("Inspections: ", Inspection[i].file_name, Inspection[i+1].file_name)
            if debugon: print(mj0)
            if debugon: print('j= ', j, ', match joit0: ', mj0, ', match joint 1: ', join_in_df1['Match'].values )
            if debugon: print('Zjoint 0: ', Zj0 )
            
            # if ( dr[join_in_df1]>5 ):
            #     print('joit0: ', J0, 'joint 1: ', Inspection[i+1].df_joints.tube_num.iloc[join_in_df1] )
            #     print("warning finding joint0: ", jointi0)
            #     print('joint1 ; ', Inspection[i+1].df_joints.iloc[join_in_df1], 'dr: ',dr[join_in_df1] )
                
            # Zji1 = Inspection[i+1].df_joints[Z_pos_col].iloc[join_in_df1]
            
            if debugon: print(join_in_df1)
            Zji1 = join_in_df1.Z_pos.values
            
            # print('match joit1: ', Inspection[i+1].df_joints.iloc[join_in_df1]['Match'], 'Zjoint 1: ', Zji1 )
            
            # Try Z position Zdef1
            Zdef1 = Zji1 + dZ0
            
            dr = np.abs(Zdef1 - Inspection[i+1].df_Def.Z_pos.values)
            
            #  Z defect closest to Zdef1 -> def1
            def1 = np.argmin(dr)
            
            if ( dr[def1]>tol ):
                if debugon: print("Not founded def: ", dr[def1])
                if debugon: print('def1 ; ',def1)
            else:
                match[j]=def1
                match1[def1] = j
                if debugon: print('Found def df1 = ',def1, 'def0 ', j)
        
        Inspection[ i ].df_Def['match'] = match
        Inspection[i+1].df_Def['match'] = match1
    
        match_Ins0 = np.where(match != emptint)
        match_Ins1 = match[match_Ins0]
        if debugon: print('Match0: ', match_Ins0)
        if debugon: print('Match1: ', match_Ins1)
        
    return match_Ins0, match_Ins1
    
    ##########################################################  

def CGR_Comput(Inspection, ij, match_Ins0, match_Ins1, min_CGR=0.1, max_CGR = 1.2):
    # depth_col, def_len_col , def_w_col,t_col , X_col  , Y_col ,H_col , gridzone_col , tube_num_col , tube_len_col , weld_dist_col , Z_pos_col , circ_pos_col , surf_pos_col , ERF_col , feature_col = col_names 
    
    #Corr grouth rate CGR
    for i in ij[0:-1]:
        i0=ij[i]
        i1=ij[i+1]
        d1s   = Inspection[i1].df_Def.d.values/100
        tck1s = Inspection[i1].df_Def.t.values
        
        d0   = Inspection[i0].df_Def.d.iloc[match_Ins0].values/100
        tck0 = Inspection[i0].df_Def.t.iloc[match_Ins0].values
        d1   = d1s[match_Ins1]
        tck1 = tck1s[match_Ins1]
        
        # if np.std(tck0 - tck1)
        
        t0   = Inspection[i0].date
        t1   = Inspection[i1].date
        
        if t1==t0:
            Warning('Matching error: Same inspection dates')
        
        # CGR [mm/y]
        CGR = d1s*tck1s/(t1 - t0)
        CGR[match_Ins1] = (d1*tck1 - d0*tck0)/(t1 - t0)
        CGR[CGR<min_CGR] = min_CGR
        CGR[CGR>max_CGR] = max_CGR
        # CGR [%/y]
        min_CGRp=min_CGR/max(tck1s)
        CGRp = d1s/(t1 - t0)
        CGRp[match_Ins1] = (d1 - d0)/(t1 - t0)
        CGRp[CGRp<min_CGRp] = min_CGRp
        
    return CGR, CGRp
    
    
def find_clusters(df_Def, D, debugon):
    # depth_col, def_len_col , def_w_col,t_col, X_col  , Y_col  ,H_col , gridzone_col , tube_num_col , tube_len_col , weld_dist_col , Z_pos_col , circ_pos_col , surf_pos_col , ERF_col , feature_col = col_names 
    #Interacting Defec (find clusters)
    # Using meters and rad/2
    # D = Inspection[-1].OD/1000
    
    n_def = len(df_Def)
    colony_def = np.zeros(n_def)
    cluster = []
    cluster_size = []
    started_colony = False
    for i in range(n_def-1):
        
        ## NEED TO KNNOW WHERE THE POSITION IS DEFINE IN THE DEFECT
        # For the begining (z0, theta0)
        Z0=df_Def.Z_pos.iloc[i]
        Z1=df_Def.Z_pos.iloc[i+1]
        L0=df_Def.L.iloc[i]/1000
        L1=df_Def.L.iloc[i+1]/1000
        end_def_i = Z0 + L0/2 
        dz = Z1 - L1/2 - end_def_i 
        t =  df_Def.t.iloc[i]/1000
        if dz < 2*((D*t)**.5):
            # Interaction
            Zeq = Z0 + dz/2
            Leq = (dz+L0+L1)*1000
            # For the begining (z0, theta0)
            # pi.D = 360º = 1, pi.D/1 = s/rad, s = pi.D.rad
            # D is in m
            circ = np.pi*D
            
            w0 = df_Def.W.iloc[i]/1000 / circ
            w1 = df_Def.W.iloc[i+1]/1000 / circ
            
            # 0 < 'clock pos' <1
            C0 = df_Def.clock_pos.iloc[i]
            C1 = df_Def.clock_pos.iloc[i+1]
            
            # end_def0 = C0 + w0
            # end_def1 = C1 + w1
            
            #############################
            # Essa intersecao entre defeitos precisa de desenho p entender
            # idea from: https://stackoverflow.com/questions/6821156/how-to-find-range-overlap-in-python
            # w/ the circular problem added
            rads0 = [C0 - w0/2, C1 - w1/2]
            radsf = [C0 + w0/2, C1 + w1/2]
            
            # negative means overlap
            drad = max(rads0) - min(radsf)
            
            # circular case (see iteraction_rule figure file)
            drad1 =  1 - (max(radsf) - min(rads0))
            
            drad = min(drad, drad1)
            
            d_circ = drad*np.pi*D
            
            if d_circ < (t/D)**.5:
                Weq = (drad + w0 + w1)*np.pi*D*1000
                Ceq = (C0 + w0/2)
                # if debugon: print(i, 'dz = ', dz, 'limit= ', 2*((D*t)**.5))
                # if debugon: print(i, 'd_circ = ', d_circ, 'drad= ', drad, 'limit = ', (t/D)**.5)
            # Interacting Defec
                colony_def[i] = i+1
                if started_colony:
                    cluster[-1].append(i+1)
                else:
                    # Start New Cluster
                    started_colony = True
                    cluster.append([i,i+1])
                    cluster_size.append([Leq,Weq, Zeq, Ceq])
                    
            else:
                started_colony = False
                
        elif started_colony:
            started_colony = False
            
    return cluster , colony_def, cluster_size
#################################################################

##################################################
# ver sempiric.inverse_modifiedb31g
def xxxxxxxxxxxxdef_critical_limits(dp,t,D,sige, MAOP):
    # ASME B31g based
    
    a = 2/3*dp
    P0 = 1.1*sige*2*t/D*10 *.72
    
    R = MAOP/P0
    
    #P0 * (1-amin) = MAOP
    #amin = 1 - R = 2/3*dp_max
    dp_max = (1 - R)*3/2 # (%)
    #dp_max-dp
    idx = np.where(dp> dp_max*1.2)
    M1 = R*0
    M1[idx]=R[idx]*a[idx]/(R[idx] - 1 + a[idx])
    Llim = R*np.NaN
    Llim[idx] = np.sqrt((M1[idx]**2 -1)*D*t[idx]/.8)
    
    return dp_max, Llim


#####################################
# MSOP (defect assessment)
#####################################
def comput_MSOP(D,sige,sigu,F,t,dp,L, unit = 'MPa', method=sempiric.modifiedb31g):
   
    # MAOP = 100 #bar
    thicks=[]
    # DNV RP F101 d = d+ alph*StDd (example A1)
    # d = (dp+0.21)*t
    d = (dp+0)*t
    
    try:
        Ndef = d.size
        PFs = np.zeros(Ndef)
    
        # for i in range(Ndef):
        PFs = method(D,t,L,d,sige,sigu,thicks)
        
    except:
        PFs = method(D,t,L,d,sige,sigu,thicks)
        
        
    if (unit.upper()=='BARS')|(unit.upper()=='BAR'):
        MSOP = PFs*10*F
    elif (unit.upper()=='MPA'):
        MSOP = PFs*F
    else:
        print('Unit Not Found: ', unit, ', expected: Bar or MPA')
    # print(MSOP[0])
    return MSOP

##################################################

 
def EffArea_clusters(D,sige,sigu, F, cluster_details, unit = 'MPa'):
    PF = []
    ii=[]
    n_cluster = cluster_details.id.size
    print('n_cluster',n_cluster)
    print('cluster_details.id',cluster_details.id)
    
    if n_cluster == 1:
        print(cluster_details)
        Ls = cluster_details.L[0]/1000
        t = cluster_details.t[0]/1000
        ds = cluster_details.d[0]/100
        Zs = cluster_details.Z[0]
        Zs = Zs - (np.min(Zs) - np.max(Ls))
        x0 = Zs - Ls/2
        x1 = Zs + Ls/2
        
        xx=[]
        for k in range(len(x0)):
            xx.append([x0[k], x1[k]])
        
        # print('xx, ds = ',xx, ds)
        positions, depths = cea.compute_depth_profile(xx,ds)
        
        ts = t*(1 - np.array(depths))
        
        rbp_m = np.array([positions, ts]).T
        
        PFs = sempiric.effective_area(D,t,Ls,0,sige,sigu,rbp_m)
        PF.append(np.min(PFs)*F)
        ii.append(0)
    else:
        for i in range(n_cluster):
            Ls = cluster_details.iloc[i].L[0]/1000
            t0 = cluster_details.iloc[i].t[0]/1000
            ds = cluster_details.iloc[i].d[0]/100
            Zs = cluster_details.iloc[i].Z[0]
            Zs = Zs - (np.min(Zs) - np.max(Ls))
            x0 = Zs - Ls/2
            x1 = Zs + Ls/2
            # y0 = ts*(1 - ds/100)
            # y1 = ts
            xx=[]
            # x_end = 0
            for k in range(len(x0)):
                xx.append([x0[k], x1[k]])
            positions, depths = cea.compute_depth_profile(xx,ds)
            
            # print('mx,my = ',positions, depths)
            # thicks = np.array([positions, t*(1 - np.array(depths)/100)]).T
            # print('thicks = ', thicks)
            t = np.mean(t0)
            ts = t*(1 - np.array(depths))
                    
            rbp_m = np.array([positions, ts]).T
            
            # print('rbp_m = ', rbp_m)
            # print('rbp_depth = ', rbp_m[0:,1])
            
            PFs = sempiric.effective_area(D,t,Ls,0,sige,sigu,rbp_m)
            PF.append(np.min(PFs)*F)
            ii.append(cluster_details.iloc[i].id)
            
        
    # print('PF = ', PF)
    return np.array(PF), ii
    
def  gridzone_set(gridzone, grid_l):


    g = gridzone
    gl=''
    if isinstance(g, str):
        gn = ''.join([char for char in g if char.isdigit()])
        gl = ''.join([char for char in g if char.isalpha()])
    else:
        gn = g
    
    get_gl = (gl == '')
    
    return gn, gl, get_gl



def compare_ERF_ProbF(Inspection):

    cmap = mcm.jet
    DF=pd.DataFrame()
    
    # ninsp=len(Inspection)

    
    for i in [1,2,3,4]:
        
        if i==1:
            tt='Current Inspection'
        elif i==2:
            tt='Future Assessment (5 years)'
        elif i==3:
            tt='Current Inspection,  t=11.45 mm'
        elif i==4:
            tt='Future Assessment (5 years),  t=11.45 mm'
            
        if i>2:
            i=i-2
            select=1
            sel = Inspection[i].df_Def['t']<13
            # sel = (Inspection[i].df_Def['t']<13) & (Inspection[i].df_Def['beta']>0.1)
            
        else:
            select=0
            sel = Inspection[i].df_Def['t']<99
            
        
        DF['ERF'] = Inspection[i].df_Def['ERF'][sel]
        DF['beta'] = Inspection[i].df_Def['beta'][sel]
        DF['PF'] = Inspection[i].df_Def['PF_form'][sel]
        DF['StD d'] = Inspection[i].df_Def['StD d']/Inspection[i].df_Def['d'][sel]
        DF['t'] = Inspection[i].df_Def['t'][sel].astype(str)
        DF['d'] = Inspection[i].df_Def['d'][sel]
        DF['L'] = Inspection[i].df_Def['L'][sel]
        
        fig, ax = plt.subplots(dpi=300)
        # sns.set_theme()
        sns.set_style('whitegrid')
        # sns.set_style('darkgrid', {"grid.color": ".6", 'xtick.bottom': True,'ytick.left': True} )
        # limits = [np.min(DF['PF']), np.max(DF['PF'])]
        # ax.plot(limits ,[1,1])
        
        if select==0:
            sns.scatterplot(x="PF", y="ERF", hue ="L", size ="d", sizes=(6, 80*2),
                    style = 't', ax=ax, alpha=.8, palette=cmap, data=DF )
        else:            
            sns.scatterplot(x="PF", y="ERF", hue ="L", size ="d", sizes=(6, 80*2),
                    ax=ax, alpha=.8,palette=cmap, data=DF )
        
        plt.xscale('log')
        plt.legend( loc='lower left',bbox_to_anchor=(1.05, 0))
        plt.title(tt)
        plt.savefig(tt+'.png', dpi=300, bbox_inches='tight')


def grafical_DF(Inspection, XY0=[], min_joint_dist = 0.5):


    X = Inspection.df_Def.X 
    Y = Inspection.df_Def.Y 
    
    dfg = pd.DataFrame([],columns=['X', 'Y', 'CGR', 'Match', 'Z'])
    dfg['Easting'] = X
    dfg['Northing'] = Y
    dfg['Long. dist [km]'] = Inspection.df_Def.Z_pos/1000
    
    dfg['Depth[%]'] = Inspection.df_Def.d
    dfg['Clock Position'] = Inspection.df_Def.clock_pos
    dfg['length [mm]'] = Inspection.df_Def.L
    dfg['Width [mm]'] = Inspection.df_Def.W
    dfg['MSOP [bar]'] = Inspection.df_Def['MSOP']*10
    dfg['Effective Area MSOP [bar]'] = Inspection.df_Def['MSOP_EffArea']*10
    dfg['ERF'] = Inspection.df_Def['ERF']
    dfg['Effective Area ERF'] = Inspection.df_Def['ERF_EffArea']
    dfg['t (mm)'] = Inspection.df_Def.t
    # dfg['Surface Position'] = Inspection.df_Def.d
    
    dfg['Max Safety d [%]'] = Inspection.df_Def['Max Safety d [%]']
    dfg['Critical Length '] = Inspection.df_Def['L max']
    
    
    relDist0 =  abs(Inspection.df_Def['ref_dist'].values)
    relDist1 =  Inspection.df_Def.tube_len.values - relDist0
    dfg['Relative Dist. [m]'] = np.minimum(relDist0, relDist1)
    
    dfg['Defect Tube Position'] = 'Tube'
    dfg['Defect on Joints'] = np.nan
    idx = dfg.index[dfg['Relative Dist. [m]']<min_joint_dist]
    dfg.loc[idx,'Defect Tube Position'] = 'Joint'
    dfg.loc[idx,'Defect on Joints'] = 1
    
    dfg['Clustered defects'] = Inspection.df_Def['Cluster defs']
    dfg['Cluster #'] = Inspection.df_Def['Cluster #']
    
    #############################################
    
    return dfg

def plot_seaborns(Inspection,  col_names,ij =[0,1],plot_match=1, XY0=[], min_joint_dist = 0.5, planar_plot = 1, longi_plot = 0, level2_plot=1):
    

    i=ij[-1]
    # depth_col, def_len_col , def_w_col,t_col , X_col  ,Y_col , H_col , gridzone_col , tube_num_col , tube_len_col , weld_dist_col , Z_pos_col , circ_pos_col , surf_pos_col , ERF_col , feature_col = col_names[i]
    
    # if len(XY0)==0: XY0 = [Inspection[i].df_joints.X.iloc[0],
    #                        Inspection[i].df_joints.Y.iloc[0],
    #                        Inspection[i].df_joints.H.iloc[0]]
    
    
    # X0 = XY0[0]
    # Y0 = XY0[1]
    # Z0 = XY0[2]
    
    if plot_match:
        match = Inspection[0].df_Def['match']
        match_Ins0 = np.where(match != -1)
        match_Ins1 = match.values[match_Ins0]
    
    MAOP = Inspection[0].MAOP
    
    plt.figure()
    plt.hist(Inspection[0].df_Def.d)
    plt.xlabel('Defects depths [%]')
    plt.ylabel('Frequency')
    
    
    if plot_match:
        CGR = Inspection[i].df_Def['CGR']
        CGRp= Inspection[i].df_Def['CGRp']
        
    dfg=Inspection[i].dfg
    
    if plot_match:
        dfg['CGR[mm]'] = np.round(CGR,2)
        dfg['CGR[%]'] = np.round(CGRp*100,1)
        dfg['Match'] = 'not matched'
        # dfg['Match'].iloc[match_Ins1] = 'matched'
        idx = dfg.index[match_Ins1]
        dfg.loc[idx,'Match'] = 'matched'
    
    #############################################
    
    Xpl = Inspection[0].df_joints.X 
    Ypl = Inspection[0].df_joints.Y 
    
    sns.set_style(style="white")
    # palt=sns.color_palette("flare")
    # sns.set(style="white", color_codes=True)
    
    # Setting ColorMap (from matplotlib)
    # https://matplotlib.org/stable/tutorials/colors/colormaps.html
    cmap = mcm.jet
    # cmap = mpl.cm.rainbow
    # cmap = mpl.cm.nipy_spectral_r
    
    fig_size = 4 #[3 to 8]
    
# Plot 

    if planar_plot:
        ax=sns.relplot(x="Easting", y="Northing", size ="length [mm]", hue ="Depth[%]",
                sizes=(fig_size*6, fig_size*80), alpha=.5, palette=cmap, edgecolor=None, 
                height=fig_size*1.5, data=dfg )
        plt.plot(Xpl, Ypl)
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
        
        
        if plot_match:
            sns.relplot(x="Easting", y="Northing", hue ="CGR[%]", size ="Depth[%]",
                    sizes=(fig_size*6, fig_size*80), alpha=.5, edgecolor=None, style = "Match",palette=cmap, 
                    height=fig_size*1.5, data=dfg )
            plt.plot(Xpl, Ypl)
       
        plt.tight_layout()
        plt.savefig('Geo_Loc.png', dpi=300, bbox_inches='tight')
        
        #sns.scatterplot
        
        # sns.relplot(x="Easting", y="Northing", hue ='Cluster #', size ="length [mm]",
        #         sizes=(fig_size*6, fig_size*80), alpha=.5, style = 'Cluster defects' ,
        #         height=fig_size*1.5, data=dfg)
        # plt.plot(Xpl, Ypl)
    
    df_jd=dfg.drop(dfg[np.isnan(dfg['Defect on Joints'])].index)
    # idx = dfg.index[dfg['t (mm)']<12]
    # dfg2 = dfg.loc[idx]
    
    # idx = dfg.index[dfg['t (mm)']<12]
    filters=(dfg.ERF>np.mean(dfg.ERF))
    dfg2 = dfg.loc[filters]
    
    
    
    if longi_plot:
        plt.figure()
        ax=sns.relplot(x='Long. dist [km]', y='Clock Position', size ="length [mm]", hue ='Depth[%]',
                sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap ,
                height=fig_size, data=dfg2, aspect =1.5 )
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)  # Increase top margin for title
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
        plt.title('Defects Clock Position')
        plt.savefig('Defects_Clock_Position.png', dpi=300, bbox_inches='tight')
        
        ax=sns.relplot(x='Long. dist [km]', y='Depth[%]', size ="length [mm]", hue ='Width [mm]',
                sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap ,
                height=fig_size, data=dfg2, aspect =1.5 )
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)  # Increase top margin for title
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
        plt.title('Defects Sizes')
        plt.savefig('Defects_Sizes.png', dpi=300, bbox_inches='tight')
        
        if plot_match:
            sns.relplot(x='Long. dist [km]', y='Depth[%]', hue ='CGR[mm]', size ="length [mm]",
                    sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap ,style = 'Match',
                    height=fig_size, data=dfg2, aspect =1.5 )
        
        
        ax=sns.relplot(x='Relative Dist. [m]',y='Depth[%]' , hue ='Long. dist [km]', size ="length [mm]",
                sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap , style = 'Defect Tube Position',
                height=fig_size, data=dfg2, aspect =1.5 )
        
        # plt.plot(df_jd['Long. dist [km]'],df_jd['Relative Dist. [m]']*0,marker='x',linewidth=0)
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)  # Increase top margin for title
        sns.move_legend( ax,"upper left", bbox_to_anchor=(1, 1))
        plt.title('Defects Joint Position')
        plt.savefig('Joint_Position.png', dpi=300, bbox_inches='tight')
        
        if plot_match:
            sns.relplot(x='Relative Dist. [m]', y='Depth[%]', hue ='CGR[mm]', size ="length [mm]",
                    sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap , style = 'Defect Tube Position',
                    height=fig_size, data=dfg2, aspect =1.5 )
        
        
        # sns.relplot(x='Long. dist [km]', y='Relative Dist. [m]', size= 'Depth[%]',   hue ="length [mm]",
        #         sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap , style = 'Defect on Joints',
        #         height=fig_size, data=dfg, aspect =1.5 )
        # plt.ylim(0,1)
        
        ################################
        # ASSESSMENT
        ################################
        
        ax = sns.relplot(x='Long. dist [km]', y='MSOP [bar]', size ="length [mm]", hue ='Depth[%]',
                sizes=(fig_size*6, fig_size*80), alpha=.7, palette=cmap , style =  't (mm)',
                height=fig_size, data=dfg2, aspect =1.5 , edgecolor=None)
        plt.plot(df_jd['Long. dist [km]'],df_jd['Relative Dist. [m]']*0+MAOP*10,linewidth=2)
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)  # Increase top margin for title
        plt.title('Defects ASSESSMENT')
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
        plt.savefig('Defects_ASSESSMENT.png', dpi=300, bbox_inches='tight')
        
        ax = sns.relplot(x='Long. dist [km]', y='ERF', size ="length [mm]", hue ='Depth[%]',
                sizes=(fig_size*6, fig_size*80), alpha=.7, palette=cmap , style =  't (mm)',
                height=fig_size, data=dfg2, aspect =1.5, edgecolor=None )
        plt.plot(df_jd['Long. dist [km]'],df_jd['Relative Dist. [m]']*0+1,linewidth=2)
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)  # Increase top margin for title
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
        plt.title('Defects ERF')
        plt.savefig('Defects_ERF.png', dpi=300, bbox_inches='tight')
        
        if level2_plot:

            plt.figure()
            ax=sns.relplot(x='Long. dist [km]', y='Effective Area ERF', size ="length [mm]", hue ='Depth[%]',
                    sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap ,
                    height=fig_size, data=dfg2, aspect =1.5 )
            plt.plot(df_jd['Long. dist [km]'],df_jd['Relative Dist. [m]']*0+1,linewidth=2)
            plt.tight_layout()
            plt.subplots_adjust(top=0.85)  # Increase top margin for title
            sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
            plt.title('Level 2 Assessment')
            plt.savefig('ERF_EffArea.png', dpi=300, bbox_inches='tight')
            
        # sns.relplot(x='Long. dist [km]', y='ERF', size ="length [mm]", hue ='Depth[%]',
        #         sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap , style =  't (mm)',
        #         height=fig_size, data=dfg2, aspect =1.5 )
        # plt.plot(df_jd['Long. dist [km]'],df_jd['Relative Dist. [m]']*0+1,linewidth=2)
        # plt.tight_layout()
        # plt.title('Defects ERF')
        # plt.savefig('Defects_ERF.png', dpi=300, bbox_inches='tight')
        
    # plt.figure()
    # fig, ax = plt.subplots()
    # plt.plot(dfg2['Critical Length '],dfg2['Depth[%]'],linewidth=0, marker='x', color='k', label='ERF = 1.0' )
    # g=sns.relplot(x="length [mm]", y='Depth[%]', s = 100, hue ='ERF', 
    #         sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap , style =  't (mm)',
    #         height=fig_size, data=dfg2, aspect =1.5 , legend='brief')
    # # g.ax
    # # plt.plot(dfg2['Critical Length '],dfg2['Depth[%]'],linewidth=0, marker='x', color='k', label='ERF = 1.0' )
    # plt.legend()
    
    # fig, ax = plt.subplots(dpi=300)
    ax=sns.relplot(x="length [mm]", y='Depth[%]', size =100, hue ='ERF',
            sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap , style =  't (mm)',
            height=fig_size, data=dfg2, aspect =1.5 )
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    plt.subplots_adjust(top=0.85)  # Increase top margin for title
    plt.plot(dfg2['Critical Length '],dfg2['Depth[%]'],linewidth=0, marker='x', color='k', label='Critical (ERF = 1.0)')
    
    # ax.plot(dfg2['Critical Length '],dfg2['Depth[%]'],linewidth=0, marker='x', color='k', label='Critical (ERF = 1.0)')
    # g=sns.scatterplot(x="length [mm]", y='Depth[%]', s = 100, hue ='ERF', ax=ax,
    #     sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap , style =  't (mm)',
    #      data=dfg2 )
    if i==ij[0]:
        plt.title('Current Assessment')
    elif i==ij[1]:
        plt.title('Future Assessment')
    plt.title('Defects Critical length')
    plt.savefig('Defects_Critical_Size.png', dpi=300, bbox_inches='tight')
    
    
    fig, ax = plt.subplots(dpi=300)
    ax.plot(dfg2['length [mm]'],dfg2['Max Safety d [%]'],linewidth=0,  marker='x', color='k')
    sns.scatterplot(x="length [mm]", y='Depth[%]', s = 100, hue ='ERF', ax=ax,
        sizes=(fig_size*6, fig_size*40), alpha=.5, edgecolor=None,  palette=cmap , style =  't (mm)',
         data=dfg2 )
    plt.subplots_adjust(top=0.85)  # Increase top margin for title
    plt.tight_layout()
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    plt.title('Defects Critical Depth')
    plt.savefig('Defects_Critical_Depth.png', dpi=300, bbox_inches='tight')
    
def plot_cluster(df_cluster):
    
    cmap = mcm.jet
    fig_size = 4 #[3 to 8]
    
    # df_cluster = pd.DataFrame(columns=['d', 'L', 'w', 'Z_pos', 'clock_pos', 'Cluster #', 'Cluster defects'])
    dfg = pd.DataFrame([],columns=['Depth[%]', 'length [mm]', 'Long. dist [km]', 'Clock Position'])
    dfg['Long. dist [km]'] = df_cluster.Z_pos/1000
    
    dfg['Depth[%]'] = df_cluster.d
    dfg['Clock Position'] = df_cluster.clock_pos
    dfg['length [mm]'] = df_cluster.L
    dfg['Width [mm]'] = df_cluster.W
    
    dfg['Cluster #'] = df_cluster['Cluster #']    
    dfg['Cluster defects'] = df_cluster['Cluster defs']
    dfg['Cluster defects'][ dfg['Cluster defects']>5] = 5
    dfg['Cluster defects'][ dfg['Cluster defects']==5] = '5+'
    
    dfg['ERF'] = df_cluster['ERF']
    dfg['Effective Area MSOP [bar]'] = df_cluster['MSOP_EffArea']*10
    dfg['Effective Area ERF'] = df_cluster['ERF_EffArea']
    
    
    ax=sns.relplot(x='Long. dist [km]', y='ERF', hue ='Depth[%]', size ="length [mm]",
            sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap , style = 'Cluster defects',
            height=fig_size, data=dfg, aspect =1.5 )
    plt.plot(dfg['Long. dist [km]'],dfg['ERF']*0+1,linewidth=2)

    plt.title('Level 1 Clusters assessmet')
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    # Critical adjustment for title spacing
    plt.subplots_adjust(top=0.85)  # Increase top margin for title
    plt.savefig('Defects_Clusters_Level 1.png', dpi=300, bbox_inches='tight' )
    
    ax=sns.relplot(x='Long. dist [km]', y='Effective Area ERF', hue ='Depth[%]', size ="length [mm]",
            sizes=(fig_size*6, fig_size*80), alpha=.7, edgecolor=None,  palette=cmap , style = 'Cluster defects',
            height=fig_size, data=dfg, aspect =1.5 )
    
    plt.plot(dfg['Long. dist [km]'],dfg['ERF']*0+1,linewidth=2)
    
    plt.title('Level 2 Clusters assessmet')
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    # Critical adjustment for title spacing
    plt.subplots_adjust(top=0.85)  # Increase top margin for title
    plt.savefig('Defects_Clusters_Level 2.png', dpi=300, bbox_inches='tight' )