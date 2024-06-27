# -*- coding: utf-8 -*-
"""
Created on Tue May 26 12:36:33 2020

@author: Adriano
"""


# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 16:09:29 2020

@author: Rodolfo Cabral
"""

from scipy import stats #Pacote para matemática e eng. stats é um módulo com várias dist de prob. e fun. estatisticas
# import os
import sys
sys.path.insert(1, '../')
from python_scripts.FORM import FORM as form #Criado por Adriano, olha o cód.:FORM.py
# from pdf_parameters import pdf_parameters #Criado por Adriano, olhar o cód.: pdf_parameters.py
#from G_calc import G_calc #Criado por Adriano, olhar o cód.: G_calc.py
# from scipy import stats
# import matplotlib.pyplot as plt
import numpy as np
#from effecArea import *
from timeit import default_timer as timer
import python_scripts.main_pipe_normas as semi_empiric
import python_scripts.Distribution_class as DC
'''
D = 609.6e-3 #m
t = 14.56e-3 #m
L = 531.0e-3 #m
d = 9.056e-3 #m
sige = 365.19178269e6 #MPa
sigu = 468.61314208e6 #MPa
StDtd = 0.087#Desvio Padrão da relação d/t pag.32 tab.3-5

# #W360x32.9

mt = t  ;st = mt*.03 ; tt='norm';#m espessura nominal
mSy = 1.08*sige  ;sSy = mSy*.08 ; tSy='norm';#MPa Tensão de escoamento
mSu = 1.09*sigu  ;sSu = mSu*.06 ; tSu='norm';#MPa tensão última
mL = L  ;sL = 19*st ; tL='norm';#m Comprimento do defeito
md = d  ;sd = st  ; td='norm';# Profundidade do defeito

# PRE_PROCESS
M = [mt,mSy,mSu,mL,md];

S = [st,sSy,sSu,sL,sd];
X = M;


# Array of Dist. Types
RV_type=[tt,tSy,tSu,tL,td];

# Failure Function
fun_G='defectSimpleDNV';
#fun_G='G_frame_column';

f_par = [D];


Pd = MAWP(X,f_par) #Pa

mPd = 1.05*Pd  ;sPd = mPd*.03 ; tPd='gumbel';#Pa Pressão de Projeto

#Reorganizando as variáveis aleatórias
M = [mPd,mt,mSy,mSu,mL,md];
S = [sPd,st,sSy,sSu,sL,sd];
X = M
RV_type=[tPd,tt,tSy,tSu,tL,td];


###################################################
#####Artigo: A comparative reliability ############
#study of corroded pipelines based on Monte Carlo##
#Simulation and Latin Hypercube Sampling methods###
###################################################

'''
def mawp(D,t,sige):
    return ((2*0.72*1*sige*t)/D)

# In[Aux Functions]    
def StD_func(accur=0.1,conf=0.9,insp_type='MFL',t=0, StDs=[], dates=[]):

    if insp_type.upper()=='UT':
        # StD for UT
        # acc_abs = [0.25,0.5,1.] #mm
        if t==0:
            print('Error!!!! t == 0 in StD_func, Risk Module')
        StD=np.sqrt(2)*accur/(t*stats.norm.ppf(0.5+conf/2))
    elif insp_type.upper()=='MFL':
        # StD for MFL
        # acc_rel = [0.05,0.1,0.2]
        StD=accur/(stats.norm.ppf(0.5+conf/2))
    elif insp_type.upper()=='FUTURE':
        # Std for future analysis
        dt0=dates[1]-dates[0]
        dt1=dates[2]-dates[1]
        kd = dt1/dt0
        StD = ((StDs[1]*(1+kd))**2 + (StDs[0]*kd)**2)**.5
        print('Future Std comput = ',StDs, StD)
    else:
        print('Error!!!! insp type not MFL, UT nor FUTURE')
    return StD

# In[failure_func]
def failure_func(X,method,thicks=0):
    #M=[mPd,mD,mt,mL,md,mSy]
    #semi_empiric.effective_area(de,t,L,d,sigy,sigu,thicks)
    #M = [mPd,mD,mt,mL,md,mSy, mSu, mErr];
    Pd=X[0]
    de=X[1]
    t=X[2]
    L=X[3]
    dp=X[4]
    sigy=X[5]
    
    nRV = len(X)
    if nRV>6:
        sigu=X[6]
    else:
        sigu=0
    
    if nRV>7:
        Err=X[7]
    else:
        Err=1 # no error

    # in RBP (lv2) case d turns to a modification factor
    # in Single idealized (lv1) cases it is not used
    thicks = thicks*dp
    if dp>=1:
        #monotonic_corrosion_assessment
        P0 = method(de,t,L,0.7,sigy,sigu,thicks)*Err
        
        G =  - dp - Pd + P0/Pd/10
    else:
        G = method(de,t,L,dp*t,sigy,sigu,thicks)*Err - Pd
    return G
    
# de,t,L,d,sigy,sigu = data_adapt(CorDutCase,opt='CorDutCase_2_standard')
def Reliability_pipe(D,tn,L,d,sige,sigu,Pd=0,insp_type='MFL',accuracy=0.1,conf=0.9,method = semi_empiric.modifiedb31g, asp_ratio=1, future_assessment=False, dates=[],thicks=0):
    
    # In[StD]
    # insp_type = MFL, absolute=UT 
    # accuracy = 0
    #Confidence Level
    # conf=0.9
    # def StD_func(accur=0.1,conf=0.9,insp_type=0,t=0, StDs=[], dates=[]):
    if future_assessment:
        
        # Compute std of the defect in two times [0, and 0+dt[0]]
        StDs=[0,0]
        for i in [0,1] :
            if np.size(conf)==1:
                StDs[i]=StD_func(accuracy,conf,insp_type,tn)
            else:
                StDs[i]=StD_func(accuracy[i],conf[i],insp_type[i],tn)
        
        StDtd=StD_func([],[],'FUTURE',[], StDs, dates)
    else :
        StDtd=StD_func(accuracy,conf,insp_type,tn)
        
    print('STD = '+str(StDtd) + ', COVd = '+str(StDtd/d))
    
    # print('STD = '+str(StDtd) + ', COVd = '+str(StDtd/d))
    # In[]
    
    if Pd==0:
        Pd = mawp(D,tn,sige) #MPa pressão de projeto
    ##############Parâmetros da dist.##################
    # From DNV RP F101 + A.P. Teixeira et al. / International Journal of Pressure Vessels and Piping 85 (2008) 228–237
    stdL = min(StDtd*20,L*.05)
    mPd = 1.05*Pd  ;sPd = mPd*.03 ; tPd='gumbel';#Pa Pressão de Projeto
    mD = D  ;sD = mD*.001 ; tD='lognorm';#m Diâmetro
    mt = tn  ;st = mt*.03 ; tt='lognorm';#m espessura nominal
    mL = L  ;sL = stdL ; tL='lognorm';#m Comprimento do defeito
    md = d  ;sd = StDtd  ; td='lognorm';# Profundidade do defeito
    mSy = sige*1.08  ;sSy = mSy*.08 ; tSy='lognorm';#MPa Tensão de escoamento
    mSu = sigu*1.09  ;sSu = mSu*.06 ; tSu='lognorm';#MPa tensão última
    mErr = 1; sErr = 0.05; tErr='lognorm';  # Model Error
    ###################################################
    
    # PRE_PROCESS
    M = [mPd,mD,mt,mL,md,mSy, mSu, mErr];
    S = [sPd,sD,st,sL,sd,sSy,sSu, sErr];
    
    # Array of Dist. Types
    RV_type=[tPd,tD,tt,tL,td,tSy,tSu, tErr];

    #num. de variaveis aleatorias
    nRV = len(M);

    # PARAMETROS DAS DISTRIBUIÇÕES
    P=[]
    for i in range(nRV):
        P.append(DC.pdf_parameters(M[i],S[i],RV_type[i]));
    
    #mG=G_calc(fun_G,X)
    #mG=effecArea(D,thicks,tn,StDtd,sige)
    
    ##############################
    ## FORM 
    start=timer()
    PF_form, beta, MPP, ii,alpha = form(M,RV_type,P,failure_func,method,thicks)

    duration=timer()-start
    print('Form time  = '+str(duration), 's, Reliability index beta = %.6f'%beta, 'PF_form = ',PF_form , '/n')
    #############################
    
    
    #############################
    # MONTE CARLO
    # from Sistema_Cordut.MC_script import monte_carlo
    # N = 1e6;
    # #MCarlo_script
    # PF_mc,Gs=monte_carlo(N,RV_type,P,failure_func,method)
    # print('PF Monte Carlo = %.6f'%PF_mc+'\n')
    # #############################
    # betam=-stats.norm.ppf(PF_mc)
    # print('Reliability index beta =', betam)

    return PF_form, beta, MPP, Pd, ii, alpha, StDtd

# def Risk_pipe()
#     #Safety class Low=0,Normal=1,High=2 
#     safety_class=0