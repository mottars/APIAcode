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
def StD_func(acc_rel_abs,conf,insp_type,t, StDs=[], dates=[]):

    if insp_type==1:
        # StD for UT
        acc_abs = [0.25,0.5,1.] #mm
        StD=np.sqrt(2)*acc_abs[acc_rel_abs]/(t*stats.norm.ppf(0.5+conf/2))
    elif insp_type==0:
        # StD for MFL
        acc_rel = [0.05,0.1,0.2]
        StD=acc_rel[acc_rel_abs]/(stats.norm.ppf(0.5+conf/2))
    elif insp_type==2:
        # Std for future analysis
        dt0=dates[1]-dates[0]
        dt1=dates[2]-dates[1]
        kd = dt1/dt0
        StD = ((StDs[1]*(1+kd))**2 + (StDs[0]*kd)**2)**.5
    return StD

# In[]
################### Dados #########################
# directory='RBP_files'
# files=[]
# for filename in os.listdir(directory):
#     if filename.endswith(".txt"):
#         files.append(filename)
#datas='case_9.txt' #remain thicks

# for datas in files:
#for datas in ['0391km.txt']:
    # print('##############################')
    #datas=files[0] #remain thicks
    # print(datas)
    #D=762.0 #mm
    # D=304.8*2 #mm
    #tn=22.1 #mm
    #f_u=525.3 #N/mm**2
    # f_u=651.5250 #API5LX80 
    # sigu=f_u
    #sige=400 #N/mm**2
    # sige=498.276022 #API5LX80
    #file=directory+'\\'+datas
    # file=datas
    # thicks = np.loadtxt(directory+'/'+file,delimiter='\t',dtype=np.float32)
    # L=thicks[-1,0]-thicks[0,0]


    # tns=[14.56, #0391
    # 12.58, #1373
    # 8.22, #3601
    # 6.27, #5882
    # 6.51, #6515
    # 6.51, #6598
    # 6.55, #7075
    # 6.45, #7312
    # 6.33, #7528
    # 6.63, #7613
    # 6.45, #8449
    # 6.39, #9436
    # 6.55] #rbp1

    # def thick(fname):
    #     thickness={'0391':tns[0],
    #     '1373':tns[1],
    #     '3601':tns[2],
    #     '5882':tns[3],
    #     '6515':tns[4],
    #     '6598':tns[5],
    #     '7075':tns[6],
    #     '7312':tns[7],
    #     '7528':tns[8],
    #     '7613':tns[9],
    #     '8449':tns[10],
    #     '9436':tns[11],
    #     'rbp1':tns[12]
    #     }
    #     return thickness.get(fname,'Invalid name')


    # tn=thick(datas.split('.txt')[0][0:4])
    #StDtd = 0.087#Desvio Padrão da relação d/t pag.32 tab.3-5
    # print(str(tn))
 
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
def Reliability_pipe(D,tn,L,d,sige,sigu,thicks=0,Pd=0,insp_type=0,acc_rel_abs=0,conf=0.9,method = semi_empiric.modifiedb31g, asp_ratio=1, future_assessment=False, dates=[]):
    
    # Failure Function
    #fun_G='b31grstreng'
    #fun_G='dnvrpf101'
    # if (method == 'b31g'):
    #     PF_empiric = semi_empiric.b31g(D,t,L,d,sigy,sigu)
    # elif (method == 'dnv'): 
    #     PF_empiric = semi_empiric.dnvrpf101(D,t,L,d,sigy,sigu)
    # elif (method == 'all'): 
    #     PF_empiric = [0,0,0,0,0,0]
    #     PF_empiric[0] = semi_empiric.b31g(de,t,L,d,sigy,sigu)
    #     PF_empiric[1] = semi_empiric.dnvrpf101(de,t,L,d,sigy,sigu)
    #     PF_empiric[2] = min(semi_empiric.effective_area(de,t,L,d,sigy,sigu,thicks))
    #     PF_empiric[3] = min(semi_empiric.dnv_complex_PartB(de,t,L,d,sigy,sigu,thicks))
    #     PF_empiric[4] = min(semi_empiric.effective_area(de,t,L,d,sigy,sigu,thicks))
    #     PF_empiric[5] = min(semi_empiric.dnv_complex_PartB(de,t,L,d,sigy,sigu,thicks))
    if Pd==0:
        Pd = mawp(D,tn,sige) #MPa pressão de projeto
    
    # fun_G=failure_func
    
    
    # In[StD]
    #MFL=0, UT=1
    # insp_type=1
    #Accuracy, relative=MFL, absolute=UT - position from list - 0,1,2...
    # acc_rel_abs=0
    #Confidence Level
    # conf=0.9
    # mean=0
    if future_assessment:
        # print("future_assessment")
        # print(future_assessment)
        # Compute std of the defect in two times [0, and 0+dt[0]]
        StDs=[0,0]
        for i in [0,1] :
            if np.size(conf)==1:
                StDs[i]=StD_func(acc_rel_abs,conf,insp_type,tn)
            else:
                StDs[i]=StD_func(acc_rel_abs[i],conf[i],insp_type[i],tn)
        
        StDtd=StD_func([],[],2,tn, StDs, dates)
        # StDtd=StD_func(acc_rel_abs,conf,insp_type,tn)
    else :
        StDtd=StD_func(acc_rel_abs,conf,insp_type,tn)
        
    # print('STD = '+str(StDtd) + ', COVd = '+str(StDtd/d))
    # In[]
    ##############Parâmetros da dist.##################
    # From DNV RP F101 + A.P. Teixeira et al. / International Journal of Pressure Vessels and Piping 85 (2008) 228–237
    stdL = min(StDtd*20,L*.05)
    mPd = 1.05*Pd  ;sPd = mPd*.03 ; tPd='gumbel';#Pa Pressão de Projeto
    mD = D  ;sD = mD*.001 ; tD='lognorm';#m Diâmetro
    mt = tn  ;st = mt*.03 ; tt='lognorm';#m espessura nominal
    mL = L  ;sL = stdL ; tL='norm';#m Comprimento do defeito
    md = d  ;sd = StDtd  ; td='norm';# Profundidade do defeito
    mSy = sige*1.08  ;sSy = mSy*.08 ; tSy='lognorm';#MPa Tensão de escoamento
    mSu = sigu*1.09  ;sSu = mSu*.06 ; tSu='lognorm';#MPa tensão última
    mErr = 1; sErr = 0.05; tErr='norm'  # Model Error
    ###################################################
    
    # PRE_PROCESS
    M = [mPd,mD,mt,mL,md,mSy, mSu, mErr];
    S = [sPd,sD,st,sL,sd,sSy,sSu, sErr];
    # print("M")
    # print(M)
    # print("S")
    # print(S)
    
    # Array of Dist. Types
    RV_type=[tPd,tD,tt,tL,td,tSy,tSu, tErr];


    # Failure Function (method)
    # fun_G='b31g';
    #fun_G='b31grstreng'
    #fun_G='dnvrpf101'

    #num. de variaveis aleatorias
    nRV = len(M);

    # PARAMETROS DAS DISTRIBUIÇÕES
    P=[]
    for i in range(nRV):
        P.append(DC.pdf_parameters(M[i],S[i],RV_type[i]));
    
    # M = M+np.array(S)*[1,1,-1,1,1,-1,0,-1]*1
    #print(P)
    
    #mG=G_calc(fun_G,X)
    #mG=effecArea(D,thicks,tn,StDtd,sige)
    
    ##############################
    ## FORM 
    start=timer()
    PF_form, beta, MPP, ii,alpha = form(M,RV_type,P,failure_func,method,thicks)

    duration=timer()-start
    # print('Form time  = '+str(duration))
    # print('Reliability index beta = %.6f'%beta+'\n')
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