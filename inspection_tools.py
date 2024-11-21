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



#############################################
# Match between joint position using LCRS algorithm
# Monotonic_Real_Sequences_Intersection
from Algorithms import MRSI_3D
from python_scripts import main_pipe_normas as sempiric

debugon = False
def get_spreadsheet_labels(Labels):
    
    
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
    if Labels[0].lower() == 'log dist. [m]'.lower():
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

        
    else:
        # 2017
        #'#' 'Joint number' 'Pipe length, m' 'Relative distance, m'
 # 'Absolute distance, m' 'Comments' 'Depth, %WT/OD' 'Length, mm'
 # 'Width, mm' 'WT, mm' 'Orientation, hrs : mins' 'Wall side'
 # 'ERF (B31G and BS 7910)' 'Easting, m' 'Northing, m' 'Height, m'
        if debugon: print("Columns: ", Labels)
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

    if not gridzone_col in df.columns:
        df[gridzone_col]=22

    #################################################
    # Create S position (absolut in-line length) xxxxxxxxxxxx
    # Filing blank spaces (with NaN): tube number, thicks, tube_len.
    #################################################
    #Add real positions S
    n_df = len(df)
    
    if len(XY0)==0: XY0 = [df.X[0],df.Y[0], df.H[0]]
    
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
    for i in range(n_df-1):
        dx = X[i+1]-X[i]
        dy = Y[i+1]-Y[i]
        dz = Z[i+1]-Z[i]
        section_len[i+1] = (dx**2+dy**2+dz**2)**.5
        
        # Filling tube number
        if ~np.isnan(df.tube_len[i]):
            joint_pos.append(i)
            current_tub_num = df.tube_num[i]
            current_tub_len = df.tube_len[i]
            # if np.isnan(current_tub_len):
            #     print(i)
            #     print(current_tub_num)
            #     print(current_tub_len)
            
        else:
            idx = df.index[i]
            df.loc[idx,tube_num_col] = current_tub_num
            df.loc[idx,tube_len_col] = current_tub_len
            # print(idx)
            # print(current_tub_len)

        # Filling Thicks
        if ~np.isnan(df[t_col][i]):
            current_t = df[t_col][i]
            
        else:
            idx = df.index[i]
            df.loc[idx,t_col] = current_t
        
        
    S_pos = np.cumsum(section_len) #+ df['Z_pos'][0]
    df['S_pos']=S_pos
    ##############################
    ###########################################################

    ###########################################################
    ## Filtering ML (Metal Loss) data frame
    df_Def=df.drop(df[np.isnan(df.d)].index)
    
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
    plt.savefig('anomalies_histogram.png', dpi=400)
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
    
    
def find_clusters(df_Def, D):
    # depth_col, def_len_col , def_w_col,t_col, X_col  , Y_col  ,H_col , gridzone_col , tube_num_col , tube_len_col , weld_dist_col , Z_pos_col , circ_pos_col , surf_pos_col , ERF_col , feature_col = col_names 
    #Interacting Defec (find clusters)
    # Using meters and rad/2
    # D = Inspection[-1].OD/1000
    
    n_def = len(df_Def)
    colony_def = np.zeros(n_def)
    cluster = []
    started_colony = False
    for i in range(n_def-1):
        
        ## NEED TO KNNOW WHERE THE POSITION IS DEFINE IN THE DEFECT
        # For the begining (z0, theta0)
        
        end_def_i = df_Def.Z_pos.iloc[i] + df_Def.L.iloc[i]/1000
        dz = df_Def.Z_pos.iloc[i+1] - end_def_i 
        t =  df_Def.t.iloc[i]/1000
        if dz < 2*(D*t)**.5:
            
            # For the begining (z0, theta0)
            # pi.D = 360º = 1, pi.D/1 = s/rad, s = pi.D.rad
            perimeter = np.pi*D
            
            w_rad = df_Def.W.iloc[i] / perimeter/1000
            def_i = df_Def.clock_pos.iloc[i]
            end_def_i = def_i + w_rad
            
            w_rad = df_Def.W.iloc[i+1] / perimeter/1000
            def_j = df_Def.clock_pos.iloc[i+1]
            end_def_j = def_i + w_rad
            
            #############################
            # Essa intersecao entre defeitos precisa de desenho p entender
            # idea from: https://stackoverflow.com/questions/6821156/how-to-find-range-overlap-in-python
            # w/ the circular problem added
            rads0 = [def_i, def_j]
            radsf = [end_def_i, end_def_j]
            
            # negative means overlap
            drad = max(rads0) - min(radsf)
            
            # circular case
            drad1 =  1 - (max(radsf) - min(rads0))
            
            drad = min(drad, drad1)
            
            d_circ = drad*np.pi*D
            if debugon: print(i, 'd_circ = ', d_circ, 'drad1= ', drad1, 'dz = ', dz)
            
            if drad < (t/D)**.5:
            # Interacting Defec
                colony_def[i] = i+1
                if started_colony:
                    cluster[-1].append(i+1)
                else:
                    # Start New Cluster
                    started_colony = True
                    cluster.append([i,i+1])
            else:
                started_colony = False
                
        elif started_colony:
            started_colony = False
            
    return cluster , colony_def
#################################################################


##################################################
def def_critical_limits(dp,t,D,sige, MAOP):
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
def comput_MSOP(D,t,dp,L,sige,sigu, unit = 'MPa', method=sempiric.modifiedb31g):
   
    # MAOP = 100 #bar
    thicks=[]
    # DNV RP F101 d = d+ alph*StDd (example A1)
    # d = (dp+0.21)*t
    d = (dp+0)*t
    
    try:
        Ndef = len(d)
        PFs = np.zeros(Ndef)
    
        for i in range(Ndef):
            PFs[i] = method(D,t[i],L[i],d[i],sige,sigu,thicks)
        
    except:
        PFs = method(D,t,L,d,sige,sigu,thicks)
        
        
    if (unit.upper()=='BARS')|(unit.upper()=='BAR'):
        MSOP = PFs*10*.72
    elif (unit.upper()=='MPA'):
        MSOP = PFs*.72
    else:
        print('Nao encontrada unidade: ', unit, 'Bar or MPA')
    # print(MSOP[0])
    return MSOP

##################################################

##################################################
import seaborn as sns
# import matplotlib.cm as mcm

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
        
        fig, ax = plt.subplots(dpi=400)
        # sns.set_theme()
        sns.set_style('whitegrid')
        # sns.set_style('darkgrid', {"grid.color": ".6", 'xtick.bottom': True,'ytick.left': True} )
        # limits = [np.min(DF['PF']), np.max(DF['PF'])]
        # ax.plot(limits ,[1,1])
        
        if select==0:
            sns.scatterplot(x="PF", y="ERF", hue ="L", size ="d", sizes=(6, 120*2),
                    style = 't', ax=ax, alpha=.8, palette=cmap, data=DF )
        else:            
            sns.scatterplot(x="PF", y="ERF", hue ="L", size ="d", sizes=(6, 120*2),
                    ax=ax, alpha=.8,palette=cmap, data=DF )
        
        plt.xscale('log')
        plt.legend( loc='lower left',bbox_to_anchor=(1.05, 0))
        plt.title(tt)
        plt.savefig(tt+'.png', dpi=400)

def plot_seaborns(Inspection,  col_names,ij =[0,1],plot_match=1, XY0=[], min_joint_dist = 0.5, planar_plot = 1, longi_plot = 0):
    

    i=ij[-1]
    depth_col, def_len_col , def_w_col,t_col , X_col  ,Y_col , H_col , gridzone_col , tube_num_col , tube_len_col , weld_dist_col , Z_pos_col , circ_pos_col , surf_pos_col , ERF_col , feature_col = col_names[i]
    
    if len(XY0)==0: XY0 = [Inspection[i].df_joints.X.iloc[0],
                           Inspection[i].df_joints.Y.iloc[0],
                           Inspection[i].df_joints.H.iloc[0]]
    
    
    X0 = XY0[0]
    Y0 = XY0[1]
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
    
    X = Inspection[i].df_Def.X - X0
    Y = Inspection[i].df_Def.Y - Y0
    
    if plot_match:
        CGR = Inspection[i].df_Def['CGR']
        CGRp= Inspection[i].df_Def['CGRp']
    
    dfg = pd.DataFrame([],columns=['X', 'Y', 'CGR', 'Match', 'Z'])
    dfg['X'] = X
    dfg['Y'] = Y
    dfg['Log. dist [km]'] = Inspection[i].df_Def.Z_pos/1000
    
    dfg['depth[%]'] = Inspection[i].df_Def.d
    dfg['Clock Position'] = Inspection[i].df_Def.clock_pos
    dfg['length [mm]'] = Inspection[i].df_Def.L
    dfg['MSOP [bar]'] = Inspection[i].df_Def['MSOP']*10
    dfg['ERF'] = Inspection[i].df_Def['ERF']
    dfg['t (mm)'] = Inspection[i].df_Def.t
    
    dfg['Max Safety d [%]'] = Inspection[i].df_Def['Max Safety d [%]']*100
    dfg['Critical Length '] = Inspection[i].df_Def['L max']
    
    if plot_match:
        dfg['CGR[mm]'] = np.round(CGR,2)
        dfg['CGR[%]'] = np.round(CGRp*100,1)
        dfg['Match'] = 'not matched'
        # dfg['Match'].iloc[match_Ins1] = 'matched'
        idx = dfg.index[match_Ins1]
        dfg.loc[idx,'Match'] = 'matched'
    
    relDist0 =  abs(Inspection[i].df_Def['ref_dist'].values)
    relDist1 =  Inspection[i].df_Def.tube_len.values - relDist0
    dfg['Relative Dist. [m]'] = np.minimum(relDist0, relDist1)
    
    dfg['Defect Tube Position'] = 'Tube'
    dfg['Defect on Joints'] = np.nan
    idx = dfg.index[dfg['Relative Dist. [m]']<min_joint_dist]
    dfg.loc[idx,'Defect Tube Position'] = 'Joint'
    dfg.loc[idx,'Defect on Joints'] = 1
    
    Inspection[i].df_Def['Cluster defs']= np.nan
    dfg['Cluster defs'] = Inspection[i].df_Def['Cluster defs']
    
    Inspection[i].df_Def['Cluster #']= np.nan
    dfg['Cluster #'] = Inspection[i].df_Def['Cluster #']
    #############################################
    
    Xpl = Inspection[0].df_joints.X - X0
    Ypl = Inspection[0].df_joints.Y - Y0
    
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
        sns.relplot(x="X", y="Y", size ="length [mm]", hue ="depth[%]",
                sizes=(fig_size*6, fig_size*120), alpha=.5, palette=cmap, 
                height=fig_size*1.5, data=dfg )
        plt.plot(Xpl, Ypl)
        
        
        if plot_match:
            sns.relplot(x="X", y="Y", hue ="CGR[%]", size ="depth[%]",
                    sizes=(fig_size*6, fig_size*120), alpha=.5, style = "Match",palette=cmap, 
                    height=fig_size*1.5, data=dfg )
            plt.plot(Xpl, Ypl)
       
    
        plt.savefig('Geo_Loc.png', dpi=400)
        
        #sns.scatterplot
        
        # sns.relplot(x="X", y="Y", hue ='Cluster #', size ="length [mm]",
        #         sizes=(fig_size*6, fig_size*120), alpha=.5, style = 'Cluster defs' ,
        #         height=fig_size*1.5, data=dfg)
        # plt.plot(Xpl, Ypl)
    
    df_jd=dfg.drop(dfg[np.isnan(dfg['Defect on Joints'])].index)
    idx = dfg.index[dfg['t (mm)']<12]
    dfg2 = dfg.loc[idx]
    
    if longi_plot:
        plt.figure()
        sns.relplot(x='Log. dist [km]', y='Clock Position', size ="length [mm]", hue ='depth[%]',
                sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap ,
                height=fig_size, data=dfg, aspect =2 )
        plt.title('Defects Clock Position')
        plt.savefig('Defects_Clock_Position.png', dpi=400)
        
        sns.relplot(x='Log. dist [km]', y='depth[%]', size ="length [mm]",
                sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap ,
                height=fig_size, data=dfg, aspect =2 )
        plt.title('Defects Sizes')
        plt.savefig('Defects_Sizes.png', dpi=400)
        
        if plot_match:
            sns.relplot(x='Log. dist [km]', y='depth[%]', hue ='CGR[mm]', size ="length [mm]",
                    sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap ,style = 'Match',
                    height=fig_size, data=dfg, aspect =2 )
        
        sns.relplot(x='Log. dist [km]', y='depth[%]', hue ='Cluster #', size ="length [mm]",
                sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style = 'Cluster defs',
                height=fig_size, data=dfg, aspect =2 )
        plt.title('Defects Clusters')
        plt.savefig('Defects_Clusters.png', dpi=400)
        
        sns.relplot(x='Log. dist [km]',y='depth[%]' , hue ='Relative Dist. [m]', size ="length [mm]",
                sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style = 'Defect Tube Position',
                height=fig_size, data=dfg, aspect =2 )
        
        plt.plot(df_jd['Log. dist [km]'],df_jd['Relative Dist. [m]']*0,marker='x',linewidth=0)
        plt.title('Defects Joint Position')
        plt.savefig('Joint_Position.png', dpi=400)
        
        if plot_match:
            sns.relplot(x='Relative Dist. [m]', y='depth[%]', hue ='CGR[mm]', size ="length [mm]",
                    sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style = 'Defect Tube Position',
                    height=fig_size, data=dfg, aspect =2 )
        
        
        # sns.relplot(x='Log. dist [km]', y='Relative Dist. [m]', size= 'depth[%]',   hue ="length [mm]",
        #         sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style = 'Defect on Joints',
        #         height=fig_size, data=dfg, aspect =2 )
        # plt.ylim(0,1)
        
        ################################
        # ASSESSMENT
        ################################
        
        sns.relplot(x='Log. dist [km]', y='MSOP [bar]', size ="length [mm]", hue ='depth[%]',
                sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style =  't (mm)',
                height=fig_size, data=dfg, aspect =2 )
        plt.plot(df_jd['Log. dist [km]'],df_jd['Relative Dist. [m]']*0+MAOP,linewidth=6)
        plt.title('Defects ASSESSMENT')
        plt.savefig('Defects_ASSESSMENT.png', dpi=400)
        
        sns.relplot(x='Log. dist [km]', y='ERF', size ="length [mm]", hue ='depth[%]',
                sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style =  't (mm)',
                height=fig_size, data=dfg, aspect =2 )
        plt.plot(df_jd['Log. dist [km]'],df_jd['Relative Dist. [m]']*0+1,linewidth=6)
        plt.title('Defects ERF')
        plt.savefig('Defects_ERF.png', dpi=400)
        
        
        sns.relplot(x='Log. dist [km]', y='MSOP [bar]', size ="length [mm]", hue ='depth[%]',
                sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style =  't (mm)',
                height=fig_size, data=dfg2, aspect =2 )
        plt.plot(df_jd['Log. dist [km]'],df_jd['Relative Dist. [m]']*0+MAOP*10,linewidth=6)
        plt.title('Defects_MSOP')
        plt.savefig('Defects_MSOP.png', dpi=400)
        
        sns.relplot(x='Log. dist [km]', y='ERF', size ="length [mm]", hue ='depth[%]',
                sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style =  't (mm)',
                height=fig_size, data=dfg2, aspect =2 )
        plt.plot(df_jd['Log. dist [km]'],df_jd['Relative Dist. [m]']*0+1,linewidth=6)
        plt.title('Defects ERF')
        plt.savefig('Defects_ERF.png', dpi=400)
        
    # plt.figure()
    # fig, ax = plt.subplots()
    # plt.plot(dfg2['Critical Length '],dfg2['depth[%]'],linewidth=0, marker='x', color='k', label='ERF = 1.0' )
    # g=sns.relplot(x="length [mm]", y='depth[%]', s = 100, hue ='ERF', 
    #         sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style =  't (mm)',
    #         height=fig_size, data=dfg2, aspect =2 , legend='brief')
    # # g.ax
    # # plt.plot(dfg2['Critical Length '],dfg2['depth[%]'],linewidth=0, marker='x', color='k', label='ERF = 1.0' )
    # plt.legend()
    
    fig, ax = plt.subplots(dpi=400)
    ax.plot(dfg2['Critical Length '],dfg2['depth[%]'],linewidth=0, marker='x', color='k', label='Critical (ERF = 1.0)')
    g=sns.scatterplot(x="length [mm]", y='depth[%]', s = 100, hue ='ERF', ax=ax,
        sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style =  't (mm)',
         data=dfg2 )
    if i==1:
        plt.title('Current Assessment')
    elif i==2:
        plt.title('Future Assessment')
    plt.title('Defects Critical length')
    plt.savefig('Defects_Critical_Size.png', dpi=400)
    
    
    fig, ax = plt.subplots(dpi=400)
    ax.plot(dfg2['length [mm]'],dfg2['Max Safety d [%]'],linewidth=0, marker='.', color='r')
    sns.scatterplot(x="length [mm]", y='depth[%]', s = 100, hue ='ERF', ax=ax,
        sizes=(fig_size*6, fig_size*120), alpha=.7, palette=cmap , style =  't (mm)',
         data=dfg2 )
    
    plt.title('Defects Critical Depth')
    plt.savefig('Defects_Critical_Depth.png', dpi=400)