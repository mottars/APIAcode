# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 11:36:06 2020
Pipeline Rules
@author: Adriano
"""
import scipy.integrate as integrate
import numpy as np
from scipy.stats import norm
import pandas as pd
import matplotlib.pyplot as plt
from itertools import groupby, count
# from scipy.interpolate import interp1d
import os
# import sys
from timeit import default_timer as timer
# from numba import jit,prange
#import seaborn as sns
# insert at 1, 0 is the script path (or '' in REPL)
#sys.path.insert(1, 'C:/Users/Adriano/Google Drive/UFPE/Carreira.Acadêmica/Doutorado/code_aster_dutos')
from python_scripts.rbp_aid_funcs import rbp_from_3d


def is_valid(*vars):
    """Check if all variables are non-empty and positive (supports multidimensional inputs)."""
    for var in vars:
        # Handle numpy arrays
        if isinstance(var, np.ndarray):
            if var.size == 0:  # Empty array
                print(f"Invalid input: {var} (empty array), ")
                return False
            if not np.all(var > 0):  # Check if all elements are positive
                invalid_values = var[var <= 0]
                print(f"Invalid input: {invalid_values} (non-positive values in array)")
                return False
        # Handle lists, tuples, or nested lists
        elif isinstance(var, (list, tuple)):
            if len(var) == 0:  # Empty list
                print(f"Invalid input: {var} (empty list)")
                return False
            # Flatten nested lists and check all values
            flattened = np.array(var).flatten()
            if not np.all(flattened > 0):
                invalid_values = flattened[flattened <= 0]
                print(f"Invalid input: {invalid_values} (non-positive values in nested list)")
                return False
        # Handle single values
        else:
            if var is None:
                print(f"Invalid input: {var} (is None)")
                return False
            if var <= 0:
                print(f"Invalid input: {var} (non-positive value)")
                return False
    return True

# In[]
def dnv_complex_PartA(data,D,t,StD,eps_d,gamma_d,gamma_m):
    #Step 0 - Pre-processor
    remainMat=integrate.simps(data[:,1],data[:,0])
    print('Material Remanescente Inspeção [mm^2]: '+str(remainMat))
    l_total=(data[-1,0]-data[0,0])
    A=(t*l_total-remainMat)
    # print(A)
    #Definir
    f_u=1
    #Step 1
    d_ave=A/l_total
    #Step 2
    Q_total=np.sqrt(1+0.31*(l_total/np.sqrt(D*t))**2)
    d_ave_sobre_t=d_ave/t+eps_d*StD
    aux1=(2*t*f_u)/(D-t)
    aux2=(1-gamma_d*(d_ave_sobre_t))/(1-gamma_d*(d_ave_sobre_t)/Q_total)
    P_total=gamma_m*aux1*aux2
    print(P_total)
    #Step 3
    # d_j=np.arange(0,max(thicks[:,1])-min(thicks[:,1]),l_total/50)
    return P_total
    
    #Step 4
# In[]
#@jit(nopython=True)
#@jit
def dnv_complex_PartB(D,t,L,d,sige,f_u,data):
    #Step 0 - Pre-processor
    remainMat=integrate.trapz(data[:,1],data[:,0])
    #print('Material Remanescente Inspeção [mm^2]: '+str(remainMat))
    l_total=(data[-1,0]-data[0,0])
    #print('l_total='+str(l_total))
    A=(t*l_total-remainMat)
#    print(A)
    #Step 1
    d_ave=A/l_total
    #print('L^2/(D*t)='+str(L/np.sqrt(D*t)))
    #print('d_ave='+str(d_ave))
    #print('d/t='+str(d/t))
    #print('d_ave/t='+str(d_ave/t))
    #Step 2
    Q_total=np.sqrt(1+0.31*(l_total/np.sqrt(D*t))**2)
    d_ave_sobre_t=d_ave/t
    aux1=(2*t*f_u)/(D-t)
    aux2=(1-(d_ave_sobre_t))/(1-d_ave_sobre_t/Q_total)
    P_total=aux1*aux2
    #print('P_total='+str(P_total))
    #Step 3
    n_subd=48 #number of subdivisions
    d_j=np.arange((t-min(data[:,1]))/n_subd,t-min(data[:,1])+(t-min(data[:,1]))/n_subd,(t-min(data[:,1]))/n_subd)
    #Step 4
    depths=pd.Series(t-data[:,1])
#    print('depths='+str(depths))
    Pj=[]
    for dj in d_j:
        #set os depths greater than dj like dj
        deph_dj=depths.copy()
        deph_dj.loc[deph_dj>dj]=dj
        A_patch=integrate.trapz(deph_dj[:],data[:,0])
#        A_patch=dj*l_total
        d_patch=A_patch/l_total
        Q_total=np.sqrt(1+0.31*(l_total/np.sqrt(D*t))**2)
        aux1=(2*t*f_u)/(D-t)
        aux2=(1-(d_patch/t))/(1-d_patch/t/Q_total)
        #Step 5
        P_patch=aux1*aux2
#        print('P_patch='+str(P_patch)+' step='+str(dj))
#        print('A_patch='+str(A_patch))
#        print('d_patch='+str(d_patch))
        #Pits analysis
        slice_depths=depths.loc[depths>dj]
        def as_range(g):
            l = list(g)
            return l[0], l[-1]
        pit_groups=([as_range(g) for _, g in groupby(slice_depths.index, key=lambda n, c=count(): n-next(c))])
        #Loop on idealized pits
        Pi=[]
        de_i=[]
        li=[]
        #Remove pontual cases
        for pg in pit_groups:
            if pg[0]==pg[1]:
                pit_groups.remove(pg)
#        print(pit_groups)
#        print(del_list)
#        del pit_groups[np.asarray(del_list)]
        de_i=[]
        li=[]
        for x0,xf in pit_groups:
            #Step 6 [(14, 30), (34, 50)] - [(9, 31), (33, 55)]
            d_i=np.mean(depths[x0:xf+1])
#            print('d_i='+str(d_i))
#            f_left=interp1d(depths.values[:x0+1],data[:x0+1,0],kind='linear',fill_value=t)
#            f_right=interp1d(depths.values[xf-1:],data[xf-1:,0],kind='linear',fill_value=t)
#            print(dj)
#            print(f_right(dj)-f_left(dj))
            li.append(data[xf,0]-data[x0,0])
#            A_i_pit=(d_i*li[-1]) #Desnecessario pois calculei di pela media
#            d_i=A_i_pit/li[-1]
            #Step 7
            te=(P_patch*D)/(2*(1.09*f_u)+P_patch)#Erro na norma - remover 1.09
            te=(P_patch*D)/(2*(f_u)+P_patch)
#            print('P_patch='+str(P_patch))
#            print('te='+str(te))
            #Step 8
            de_i.append(d_i-(t-te))
            #Step 9
            Qi=np.sqrt(1+0.31*(li[-1]/np.sqrt(D*te))**2)
            auxi1=(2*te*1.09*f_u)/(D-te)
#            auxi1=(2*te*f_u)/(D-te)
            auxi2=(1-(de_i[-1]/te))/(1-de_i[-1]/te/Qi)
            Pi.append(auxi1*auxi2)
#        print(pit_groups)
#        print(de_i)
        for n in range(len(pit_groups)):
            for m in range(len(pit_groups)):
                if n<=m:
                    #Step 10
                    de_nm=0
                    lnm=data[pit_groups[m][1],0]-data[pit_groups[n][0],0]
#                    print('comp pit='+str(lnm))
                    for i in np.arange(n,m+1):
                        #Step 11
                        de_nm=de_nm+(de_i[i]*li[i])/lnm
                    #Step 12
#                    print('de_nm='+str(de_nm))
                    Qnm=np.sqrt(1+0.31*(lnm/np.sqrt(D*te))**2)
                    auxi1=(2*te*f_u)/(D-te)
                    auxi2=(1-(de_nm/te))/(1-de_nm/te/Qnm)
                    Pi.append(auxi1*auxi2)
#        print('Pi='+str(Pi))
        # Step 13
        if Pi:
            Pj.append(min(min(Pi),P_patch,P_total))
        else: 
            Pj.append(min(P_patch,P_total))
        #Step 14 - Loop
    #Step 15 - P Single
    #Q_total=np.sqrt(1+0.31*(l_total/np.sqrt(D*t))**2)
    #dmax_sobre_t=max(depths)/t
#    print()
    
    #aux1=(2*t*f_u)/(D-t)
    #aux2=(1-dmax_sobre_t)/(1-dmax_sobre_t/Q_total)
    #P_single=aux1*aux2
#    print('Pj='+str(Pj))
    #print('P_single='+str(P_single))
#    Pj.append(P_single)
    return Pj
# In[] Testar e certificar com outros resultados da literatura
def bs7910g(D,t,L,d,sige,sigu,thicks=0):
    
    # if(D and t and L and d and sige):
    if is_valid(D,t,L,d,sige):
        M = (1+0.31*(L**2/(D*t)))**.5
        Sf = (sige+sigu)/2
        #Sf = 0.9*sigu??
        #s2 = S*(1-d/t)/(1-d/t/M)
        P0 = Sf*2*t/(D-t)
        pf=P0*(1-d/t)/(1-d/t/M)
        
        ## As in Report to TBG
        # Sf = sig_u ????
        #SafFact = f1 x f2 = 0.9x0.72
    return pf
# In[] Testar e certificar com outros resultados da literatura
def bs7910gMod(D,t,L,d,sige,sigu,thicks=0):
    
    # if(D and t and L and d and sige):
    if is_valid(D,t,L,d,sige):

        M = (1+0.31*(L**2/(D*t)))**.5
        # Sf = (sige+sigu)/2
        #s2 = S*(1-d/t)/(1-d/t/M)
        P0 = sigu*2*t/(D-t)
        pf=P0*(1-d/t)/(1-d/t/M)
    return pf
# In[]
def b31g(D,t,L,d,sige,sigu,thicks=0):
    if is_valid(D,t,L,d,sige):
    # if(D and t and L and d and sige):
        P0 = 1.1*sige*((2*t)/D)
        if (L>(20*D*t)**0.5):
            pf=P0*(1-d/t)
        else:
            M=(1+.8*(L**2/(D*t)))**0.5
            Q = 2*d/(3*t)
            pf=P0*((1-Q)/(1-Q/M))
        #SafFact = f1 = 0.72
    return pf
# In[]
def modifiedb31g(D,t,L,d,sige,sigu,thicks=0):
    # 085dL ASME B31g (2009)
    if sige<=483:
        sflow = sige+69
    else:
        sflow = sige*1.1
    P0 = sflow*((2*t)/D)
    is_valid(D,t,L,d,sige)
    # if(D and t and L and d and sige).all():
    z = L**2/(D*t) 
    # print (z)
    # print (z>50)
    # if np.all(z>50):
    #     M=0.032*z+3.3
    #     # pf=sflow*((2*t)/D)*(1-d/t)
    # else:
    #     M=(1+.6275*z-0.003375*(z**2))**0.5
    M = np.where(z > 50, 
                 0.032 * z + 3.3,
                 (1 + 0.6275 * z - 0.003375 * (z**2))**0.5)
    Q = 0.85*d/t
    pf=P0*((1-Q)/(1-(Q/M)))
    return pf

# In[]
def inverse_modifiedb31g(D, sige, sigu, t, L, d,  pf, thicks=0):
    
    if is_valid(D,t,L,d,sige):
        # print('D, sige, sigu, t, L, d,  pf',D, sige, sigu, t, L, d,  pf)

        # Calculate sflow based on sige
        # if sige <= 483:
        #     sflow = sige + 69
        # else:
        #     sflow = sige * 1.1
            
        sflow = np.where(sige <= 483, sige + 69, sige * 1.1)
        
        P0 = sflow * ((2 * t) / D)
        z = L**2 / (D * t)
        
        # print (z)
        M = np.where(z > 50, 
                     0.032 * z + 3.3,
                     (1 + 0.6275 * z - 0.003375 * (z**2))**0.5)
        # if z > 50:
        #     M = 0.032 * z + 3.3
        # else:
        #     M = (1 + 0.6275 * z - 0.003375 * (z**2))**0.5
        
        # Let's denote A = pf / P0
        R = pf / P0
        
        # print(M,R)
        # Now, solve for Q:
        Q = (R - 1) / (R / M - 1)
        # print(Q)
        d_max = (Q * t) / 0.85
        d_max = np.where(d_max>t, t, d_max)
        
        # dp_max = d_max/t*100
        # dp_max = np.where(dp_max>100, 100, dp_max)
        ###############################################
        
        # For L_max
        Q = 0.85 * d / t
        M = R / ((R - 1) / Q + 1)
        
        # We need to solve for z in both cases and check which one is valid.
        # Case 1: z > 50
        z_case1 = (M - 3.3) / 0.032
        
        # if z_case1 > 50:
        #     z = z_case1 
        # else:
            
        # Case 2: z <= 50
        # M = (1 + 0.6275 * z - 0.003375 * z**2)**0.5
        # Square both sides:
        # M^2 = 1 + 0.6275 * z - 0.003375 * z^2
        # Rearrange:
        # 0.003375 * z^2 - 0.6275 * z + (1 - M^2) = 0
        # Solve the quadratic equation for z:
        a = 0.003375
        b = -0.6275
        c = 1 - M**2
        discriminant = b**2 - 4 * a * c
        if np.any(discriminant < 0):
            print('discriminant < 0 - > ',np.where(discriminant) < 0)
            raise ValueError("No valid solution for z (discriminant < 0).")
        
        z_case2 = (-b + discriminant**0.5) / (2 * a)
        # z2 = (-b - discriminant**0.5) / (2 * a)
    
        # Choose the valid z (positive and <= 50)
        # if z1 > 0 :
        #     z = z1
        # else :
        #     z =  (-b - discriminant**0.5) / (2 * a)
        #     raise ValueError("No make sense solution for z1 < 0 ?.")
        
        z = np.where(z_case1 > 50, z_case1, z_case2)
        
        # Now, solve for L using z = L^2 / (D * t)
        L_max = (z * D * t)**0.5
    
    return d_max, L_max
# In[]
def dnvrpf101(D,t,L,d,sige,sigu,thicks=0):
    if is_valid(D,t,L,d,sigu):
    # if(D and t and L and d and sigu):
        M=(1+.31*(L**2/(D*t)))**0.5
        pf=sigu*(2*t/(D-t))*((1-d/t)/(1-d/(t*M)))
    return pf

#@jit(nopython=True) 
def effective_area(D,t,L,d,sige,sigu,thicks):
    def pf(sige,t,D,A_cor,A0,L_ef):
        if (L_ef**2/(D*t)>50):
            M=0.032*(L_ef**2/(D*t))+3.3
        else:
            M=(1+.6275*(L_ef**2/(D*t))-0.003375*(L_ef**4/(D**2*t**2)))**0.5
        
        if A0 and M and A_cor/(A0*M) < 1 :
            R = (1-A_cor/A0) / (1-A_cor/(A0*M))
        else:
            R = 1
        pf=(sige+69)*((2*t)/D)*R
        return pf
    
    Pj=[]
    
    depths=t-thicks[0:,1]
    # print('depths = ', depths)
    is_valid(D,t,sige,depths)
    # print(thicks)
    # print('len thicks = ',len(thicks))
    # print('Total, D,t,sige , depths1', D,t,sige,depths[0])
    for i in range(len(thicks)):
        for j in range(len(thicks)-i-1):
#            print(j,i,len(thicks-i-2))
            L_ef=thicks[j+i+1,0]-thicks[j,0]
            if L_ef > 0:
                A_cor=integrate.trapz(depths[j:j+i+1],thicks[j:j+i+1,0])
                A0=L_ef*t
    #            print(L_ef,A_ef,A0)
                pfi=pf(sige,t,D,A_cor,A0,L_ef)
                # if pfi<13:
                #     print('pfi, L, d, ', pfi, L_ef, A_cor/A0, 1-A_cor/A0)
                #     print('i,j, ', i, j)
                # print(pfi)
                Pj.append(pfi)
    return Pj

    
# In[Aux Functions]
def StD_func(acc_rel_abs,conf,insp_type,t):
    if insp_type:
        #StD for UT
        StD=np.sqrt(2)*acc_rel_abs/(t*norm.ppf(0.5+conf/2))
    else:
        #StD for MFL
        StD=acc_rel_abs/(norm.ppf(0.5+conf/2))
    return StD
def gamma_m(inputs):
        gammas=[0.79,0.74,0.7,0.82,0.77,0.72]
        gamma_m={
        '00':gammas[0],
        '01':gammas[1],
        '02':gammas[2],
        '10':gammas[3],
        '11':gammas[4],
        '12':gammas[5]}
        return gamma_m.get(inputs,'Invalid input')
def gamma_eps_d(acc_rel_abs,conf,insp_type,t):
    StD_0=StD_func(acc_rel_abs,conf,insp_type,t)
    if StD_0<=0.16:
        if insp_type==0:
            gamma_d=1.2
        elif insp_type==1:
            gamma_d=1+4.6*StD_0-13*9*StD_0**2
        elif insp_type==2:
            gamma_d=1+4.3*StD_0-4*1*StD_0**2
        eps_d=-1.33+37.5*StD_0-104.2*StD_0**2
    if (0.04<=StD_0<0.08)&(insp_type==0):
            gamma_d=1+5.5*StD_0-37.5*StD_0**2       
    if (StD_0<0.04):
        if (insp_type==0):
            gamma_d=1+4*StD_0
        eps_d=0
    return gamma_d, eps_d

# In[]
def run_database_cases():
    print('DNV Complex PartB')
    dbname='pipeDatabase.pkl'
    db_dir='C:/Users/Adriano/Google Drive/UFPE/Projeto.Dutos/python/PipeBurst/database'
    database=pd.read_pickle(db_dir+'/'+dbname)
    files=[]
    directory = 'C:/Users/Adriano/Google Drive/UFPE/Carreira.Acadêmica/Doutorado/code_aster_dutos/3dreal_thicks_data'
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            files.append(filename)
    for datas in files:     
        Jobname=datas.split('.txt')[0]
        thicks = rbp_from_3d(directory,datas)
        fig=plt.figure()
        plt.plot(thicks[:,0],thicks[:,1],'-',color='darkgrey')
        plt.ylim(0,1.2*max(thicks[:,1]))
        plt.ylabel('Pipe Wall Thickness [mm]')
        plt.xlabel('Corrosion Lenght [mm]')
        plt.fill_between(thicks[:,0],np.zeros(len(thicks[:,1])),thicks[:,1],color='lightgrey')
        fig.savefig(Jobname+'.jpg', format='jpg',quality=95,dpi=300)
#        print(thicks)
        D=database.loc[database.file==datas].D.values[0]
        t=database.loc[database.file==datas].t.values[0]
        su=np.array(database.loc[database.file==datas].su.values[0])
        L=thicks[-1,0]-thicks[0,0]
        d=database.loc[database.file==datas].dmax.values[0]
        sy=database.loc[database.file==datas].sy.values[0]
        print('Pipe='+str(Jobname))
        print('D='+str(D))
        print('t='+str(t))
        print('sig_u='+str(su))
        factor_sflow=1
        sflow=factor_sflow*su
        Pj=dnv_complex_PartB(D,t,L,d,sy,sflow,thicks)
        print('Failure Pressure (DNV Complex B)='+str(min(Pj)))
        pfb31g=b31g(D,t,L,d,sy,sigu,thicks)
        print('Failure Pressure (B31G)='+str(pfb31g))
        # pfb31grstreng=b31grstreng(D,t,L,d,sige,su,thicks)
        # print('Failure Pressure (B31G RStreng 0.85)='+str(pfb31grstreng))
        # pfdnvrpf101=dnvrpf101(D,t,L,d,sige,su,thicks)
        # print('Failure Pressure (DNV Single)='+str(pfdnvrpf101))
        # pfeffective_area=effective_area(D,t,L,d,sige,su,thicks)
        # print('Failure Pressure (Effective Area)='+str(min(pfeffective_area)))
#        return thicks

def run_all():
    normas=['bs7910g','bs7910gMod','b31g','dnvrpf101','dnv_complex_PartB','effective_area','b31grstreng']
    Pj=[]
    for kk, norma in enumerate(normas):
        try:
            L=xxx
        except NameError:
            L=(thicks[-1,0]-thicks[0,0])
            print("Complex Defects - Calculating L")
        try:
            d=xxx
        except NameError:
            d=t-np.amin(thicks[:,1])
            print("Complex Defects - Calculating d")
        # dictionary create
#        kwargs={'D':D,'t':t,'L':L,'d':d,'sige':sige,'sigu':sigu,'thicks':thicks}
        Pj.append(norma(D,t,L,d,sige,sigu,thicks))
        if  isinstance(Pj[-1], list):
            plt.figure()
            plt.plot(Pj[-1],'-')
            print('Failure Pressure('+str(norma.__name__)+')='+str(min(Pj[-1])))
        else:
            print('Failure Pressure('+str(norma.__name__)+')='+str((Pj[-1])))

if __name__ == '__main__':

    OD = 14*25.4
    t0 = 6.4
    Po = 7.97
    D = OD/1000
    t = t0/1000
    L = 0.118
    d = t*.46
    
    F = 0.72
    pipe_data = (0.35559999999999997, 0.0064, 323.412, 442.934)
    [dm, Llim] = inverse_modifiedb31g(D, 323.412, 442.934, t, L, d, Po/F)
    # dm = dp_max/100*t
    P0 = modifiedb31g(D,t,L,d,323.412, 442.934)
    Ps = modifiedb31g(D,t,L,dm,323.412, 442.934)
    # Ps = itools.comput_MSOP(*pipe_data, 1, t0/2000, OD/1000)
    
    print('Pmax = ', Po)
    print('d0 , Pmax0 = ', d/t , P0*F)
    print('dcrit , Pmcrit = ', dm/t , Ps*F)
    
        
    if 0:
        # In[DNV Example10]
        directory=''
        #datas='DNV_complex_example10.txt' #Depths not remain thicks
        # file=r'C:\Users\juliop\Documents\cordut-2019-02\trunk\Sistema_Cordut\Modeller\Real_Defect\Reais_Exemp\160.txt' #remain thicks
        # D=762.0 #mm
        # t=22.1 #mm
        # f_u=525.3 #N/mm**2
        # sigu=f_u
        # sige=400 #N/mm**2
        # #file=directory+'\\'+datas
        # file=datas
        # depths = np.loadtxt(file,delimiter='\t')
        # thicks=depths
        #thicks[:,1]=t-thicks[:,1] #depths2thicks
        # In[]
    
        directory='.'
        file='TS02.txt'
        D = 813
        t = 11.45
        # thicks=rbp_from_3d(r'C:\Users\juliop\Documents\cordut-2019-02\trunk\Sistema_Cordut\Modeller\Real_Defect\Reais_Exemp', i)[0]
        # atencao!!!! normas tem que ser transpostas mas o codeaster nao precisa
        thicks = rbp_from_3d(directory,file)
        # print(thicks)
        # thicks=np.transpose(np.array(thicks))
        
        sigu = 565.4 
        sige = 482.6
        # In[Confiability]
        #MFL=0, UT=1
        insp_type=1
        #Accuracy, relative=MFL, absolute=UT
        acc_rel_abs=0.5
        #Safety class Low=0,Normal=1,High=2 
        safety_class=0
        #Confidence Level
        conf=0.9
    
        # gamma_m=gamma_m(str(insp_type)+str(safety_class))
        gamma_d,eps_d=gamma_eps_d(acc_rel_abs,conf,insp_type,t)
        StD=StD_func(acc_rel_abs,conf,insp_type,t)
    
        # In[Run]
    
    
    
        #run_all(D,t,L,d,sige,sigu,thicks) 
        #run_all()          
        #plt.plot(thicks[:][0],thicks[:][1],'-')
        #Pj=dnv_complex_PartA(thicks,D,t,StD,eps_d,gamma_d,gamma_m)
        #Pj=dnv_complex_PartB(thicks,D,t,f_u)
        # print('thicks = ',thicks)
        L=(thicks[-1,0]-thicks[0,0])
        d=t-np.amin(thicks[:,1])
        start = timer()
        Pjs=effective_area(D,t,L,d,sige,sigu,thicks)
        PF = np.min(Pjs)
        print('PF eff Area: ',PF)
        # run_all()
        duration = timer() - start
        print(duration)
        # print('Failure Pressure='+str(min(Pj)))
        #plt.plot(Pj,'-')
    
        #kwargs unpacking
        #def a(**kwargs):
        #    print(kwargs['bola'])
        #a(**{"bola":[31,2,3]})    
    
        #D = 812.8
        #t = 19.10# mm
        #f_u = 530.9 #N/mm2 (X65)
        #l = 203.2 #mm
        #d = 13.4 #mm

