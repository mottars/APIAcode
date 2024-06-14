# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 20:33:13 2019
Main function for create rpb cases to aster
@author: Adriano
210120 -Corrigir PLong para tracao, situacao atual compressao
"""
import rbp_gen as rg
import numpy as np
import os
import pickle
import adjustDistribution as aD
import pandas as pd
import scipy.stats as st
import scipy as sp
import time
import sys
import datetime as dt
#sys.path.insert(1, 'C:/Users/Adriano/Google Drive/UFPE/Carreira.Acadêmica/Doutorado/code_aster_dutos')
# from rbp_aid_funcs import rbp_from_3d
from Curves import curves
from scipy.stats import norm


def gen_random_cases():
    clusterrun=1 # if will run on cluster set to 1
    ###############################################################################
    #Adjust Distribution for data in path dir_files2ad
    adj_data=False
    #adj_data=True
    fitfile='best_fit.pkl'
    
    if adj_data or (not os.path.exists(fitfile)):  
        dir_files2ad = 'adjust_dist'
        best_fit=aD.adjDist(dir_files2ad)
        #save data
        best_fit.to_pickle(fitfile)
    #read existent data
    best_fit=pd.read_pickle(fitfile)
    rand_thicks=[]
    data_seed=[] #filename of data used for generate random samples
    for i in range(len(best_fit)):
        dataname=best_fit.loc[i]['Data']
        print(dataname)
        params=best_fit.loc[i]['Fit Params']
        print(params)
        arg = params[:-2]
        loc = params[-2]
        scale = params[-1]
        best_fit_name=best_fit.loc[i]['Best_Dist']
        print(best_fit_name)
        best_dist = getattr(st, best_fit_name)
        thicks=best_fit.loc[i]['Thicks'].values
        sizethicks=len(thicks)
        sample_len=400
        ft=0.7#factor_thick
    #    lim=max(thicks)
        lim=min(thicks)
        for j in range(sample_len):
            rt=best_dist.rvs(*arg,loc=loc,scale=scale,size=sizethicks)
            n_minthick=len(rt[rt<ft*lim])
            while n_minthick>0:
                rt[rt<ft*lim]=best_dist.rvs(*arg,loc=loc,scale=scale,size=len(rt[rt<ft*lim]))
                n_minthick=len(rt[rt<ft*lim])
            rand_thicks.append([best_fit.loc[i]['Long Coords'].values,rt])
            data_seed.append(dataname)
    ########################################3
    #?????? Salvar nome do arquivo de malha gerado 0391km_2019-07-24...        
    randsample={'Rand Thicks':rand_thicks,'Data seed':data_seed}
    thicks_samples=pd.DataFrame(randsample,columns=['Rand Thicks','Data seed'])
    thicksfile='thicks_samples.pkl'
    thicks_samples.to_pickle(thicksfile)
    ###############################################################################
    re=304.8
    t=[14.56, #0391
       12.58, #1373
       8.22, #3601
       6.27, #5882
       6.51, #6515
       6.51, #6598
       6.55, #7075
       6.45, #7312
       6.33, #7528
       6.63, #7613
       6.45, #8449
       6.39, #9436
       6.55] #rbp1
    
    def thick(fname):
        thickness={'0391':t[0],
        '1373':t[1],
        '3601':t[2],
        '5882':t[3],
        '6515':t[4],
        '6598':t[5],
        '7075':t[6],
        '7312':t[7],
        '7528':t[8],
        '7613':t[9],
        '8449':t[10],
        '9436':t[11],
        'rbp1':t[12]}
        return thickness.get(fname,'Invalid name')
    pipes_inputs=[]
    thicks_list=[]
    for i in range(len(thicks_samples)):
        thickcase=thicks_samples.loc[i]['Data seed']
        pipes_inputs.append([re/1000,thick(thickcase[0:4])/1000]) #mm to m
    
    for pi,ts,ds in zip(pipes_inputs,thicks_samples['Rand Thicks'],thicks_samples['Data seed']):
        pipe_input=pi
        thicks=ts
        ts[0]=ts[0]/1000 #mm to m
        ts[1]=ts[1]/1000 #mm to m
        L=2.5*max(ts[0])
        d_or_r=1 #0 - input diameters, 1 - input radius and thickness
        ##loc 0 - external, 1- internal
        loc=0
        bound_smooth=0
        restrito=1
        loadtemp=0
        dir_to_save='C:\\Users\\Adriano\\Documents\\VirtualBoxComp\\Mint\\aster\\'
    #    dir_to_save=os.getcwd()+'\\aster\\'
        Jobname=ds
        curve_default=os.getcwd()+'/curves/'+'CurveX80_py.cf'
        curve=curve_default
        rg.aster_rbp(pipe_input,d_or_r,L,thicks,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save,clusterrun)
        time.sleep(1)

#pipe_input=[0.3048,0.01456]
def gen_simplecase():
    from os.path import expanduser
    home = expanduser("~") # generic home directory
    clusterrun=0 # if will run on cluster set to 1
    pipe_input=[10,1]
#    thicks=thicks_samples.loc[0]['Rand Thicks']
    ##Pipe Lenght
    L=20
    d_or_r=1 #0 - input diameters, 1 - input radius and thickness
    thicks=[list(np.linspace(0,4,5)),[0.9,.8,.6,.8,0.9]]
    #thicks=[list(thicks[0]),thicks[1]]
    ##loc 0 - external, 1- internal
    loc=0
    bound_smooth=1
    restrito=1
    loadtemp=0
    ##dir_to_save='/home/dayvson/Documentos/prp2aster/'
    #dir_to_save=os.getcwd()+'\\aster\\'

    dir_to_save=home+'/Ficus/save/'
    Jobname='test'
    curve_default=os.getcwd()+'/curves/'+'CurveX80_py.cf'
    curve=curve_default
#    pintNodeList,elements=rg.aster_rbp(pipe_input,d_or_r,L,thicks,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save,clusterrun)
    rg.aster_rbp(pipe_input,d_or_r,L,thicks,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save,clusterrun)
#    return pintNodeList,elements

    
def gen_multiples_cases():
    clusterrun=1 # if will run on cluster set to 1
    re=304.8
    t=[14.56, #0391
       12.58, #1373
       8.22, #3601
       6.27, #5882
       6.51, #6515
       6.51, #6598
       6.55, #7075
       6.45, #7312
       6.33, #7528
       6.63, #7613
       6.45, #8449
       6.39, #9436
       6.55] #rbp1
    
    def thick(fname):
        thickness={'0391':t[0],
        '1373':t[1],
        '3601':t[2],
        '5882':t[3],
        '6515':t[4],
        '6598':t[5],
        '7075':t[6],
        '7312':t[7],
        '7528':t[8],
        '7613':t[9],
        '8449':t[10],
        '9436':t[11],
        'rbp1':t[12]}
        return thickness.get(fname,'Invalid name')
    files=[]
    directory = 'adjust_dist'
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            files.append(filename)
    for datas in files:        
        # Load data from statsmodels datasets
        #data = pd.Series(sm.datasets.elnino.load_pandas().data.set_index('YEAR').values.ravel())
    #    data = np.loadtxt(directory+'/'+datas,delimiter='\t')
        data = pd.Series(np.loadtxt(directory+'/'+datas,delimiter='\t')[:,1])
        longcoord=pd.Series(np.loadtxt(directory+'/'+datas,delimiter='\t')[:,0])
        pipe_input=[re/1000,thick(datas.split('.txt')[0][0:4])/1000]
        thicks=[list(longcoord.copy()/1000),list(data.copy()/1000)]
        L=2.5*max(longcoord/1000)
        d_or_r=1 #0 - input diameters, 1 - input radius and thickness
        ##loc 0 - external, 1- internal
        loc=0
        bound_smooth=0
        restrito=1
        loadtemp=0
        dir_to_save='C:\\Users\\Adriano\\Documents\\VirtualBoxComp\\Mint\\aster\\'
    #    dir_to_save=os.getcwd()+'\\aster\\'
        Jobname=datas.split('.txt')[0]
        curve_default=os.getcwd()+'/curves/'+'CurveX80_py.cf'
        curve=curve_default
#        print((pipe_input,d_or_r,L,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save))
        rg.aster_rbp(pipe_input,d_or_r,L,thicks,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save,clusterrun)
# In[Read Test ]
def gen_database_cases():
    clusterrun=0 # if will run on cluster set to 1
    dbname='pipeDatabase.pkl'
    db_dir='C:/Users/Adriano/Google Drive/UFPE/Projeto.Dutos/python/PipeBurst/database'
    database=pd.read_pickle(db_dir+'/'+dbname)
    files=[]
    directory = 'C:/Users/Adriano/Google Drive/UFPE/Carreira.Acadêmica/Doutorado/code_aster_dutos/3dreal_thicks_data'
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            files.append(filename)
    for datas in files:        
    #    data = np.loadtxt(directory+'/'+datas,delimiter='\t')
        Jobname=datas.split('.txt')[0]
        print(Jobname)
        temp=rbp_from_3d(directory,datas)
        dmax=database.loc[database.file==datas].dmax.values[0]
        t=database.loc[database.file==datas].t.values[0]
        if (t-np.amin(temp[:,1]))<dmax:
            print('changing min remain thick')
            print(temp[np.argmin(temp[:,1]),1])
            temp[np.argmin(temp[:,1]),1]=t-dmax
#            print(dmax)
#            print(t-np.amin(temp[:,1]))
#            print(t-dmax)
#        print(t-np.amin(data))
        data = pd.Series(temp[:,1])
        longcoord=pd.Series(temp[:,0])
        re=database.loc[database.file==datas].D.values[0]/2       
        sigy=np.array([database.loc[database.file==datas].sy.values[0]])
        sigu=np.array([database.loc[database.file==datas].su.values[0]])
        defy=np.array([database.loc[database.file==datas].defy.values[0]])
        defu=np.array([database.loc[database.file==datas].defu.values[0]])
        
        E=np.array([database.loc[database.file==datas].E.values[0]])
        pipe_input=[re/1000,t/1000]
        thicks=[list(longcoord.copy()/1000),list(data.copy()/1000)]
        #Comprimento do modelo (norma 2.5*tamMax)
        L=2.5*max(longcoord/1000)
        
#        L=max(longcoord/1000)+1
#        print('Comprimento do Modelo='+str(L))
        d_or_r=1 #0 - input diameters, 1 - input radius and thickness
#        loc 0 - external, 1- internal
        loc=1
        bound_smooth=0
        restrito=0
        loadtemp=0
        dir_to_save='C:\\Users\\Adriano\\Documents\\VirtualBoxComp\\Mint\\aster\\'
#    #    dir_to_save=os.getcwd()+'\\aster\\'
        
#        print(E)
#        print(E*defu/sigu)
#        curve_default=os.getcwd()+'/curves/'+'CurveX80_py.cf'
        dirCusave=os.getcwd()+'/curves/'
#        Ar, n, yo, Stress, Def, Stressi, Defi = curves(sigy,sigu,defy,defu,E,Jobname,dirCusave)
        curve=dirCusave+'Curve'+Jobname+'_py'+'.cf'
#        print(Stressi)
#        print(Defi)
        print((pipe_input,d_or_r,L,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save))
        rg.aster_rbp(pipe_input,d_or_r,L,thicks,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save,clusterrun)
    return database,datas

def gen_multiples_cases_bythicks():
    clusterrun=1 # if will run on cluster set to 1
    re=304.8
    t=[14.56, #0391
       12.58, #1373
       8.22, #3601
       6.27, #5882
       6.51, #6515
       6.51, #6598
       6.55, #7075
       6.45, #7312
       6.33, #7528
       6.63, #7613
       6.45, #8449
       6.39, #9436
       6.55] #rbp1
    
    def thick(fname):
        thickness={'0391':t[0],
        '1373':t[1],
        '3601':t[2],
        '5882':t[3],
        '6515':t[4],
        '6598':t[5],
        '7075':t[6],
        '7312':t[7],
        '7528':t[8],
        '7613':t[9],
        '8449':t[10],
        '9436':t[11],
        'rbp1':t[12]}
        return thickness.get(fname,'Invalid name')
    files=[]
    directory = 'adjust_dist'
    for filename in os.listdir(directory):
        if filename=='rbp1.txt': #force file
#        if filename.endswith(".txt"):
            files.append(filename)
    for datas in files:  
        longcoord=pd.Series(np.loadtxt(directory+'/'+datas,delimiter='\t')[:,0])
        # Load data from statsmodels datasets
        #data = pd.Series(sm.datasets.elnino.load_pandas().data.set_index('YEAR').values.ravel())
    #    data = np.loadtxt(directory+'/'+datas,delimiter='\t')
        read_thicks_rand=1
        if read_thicks_rand:
             with open("kde_dist_rbp1.txt", "rb") as fp:   # Unpickling
                 thicks_rand = pickle.load(fp)
        for i in thicks_rand:
            data =  pd.Series(i[0,:])
            pipe_input=[re/1000,thick(datas.split('.txt')[0][0:4])/1000]
            thicks=[list(longcoord.copy()/1000),list(data.copy()/1000)]
            L=2.5*max(longcoord/1000)
            d_or_r=1 #0 - input diameters, 1 - input radius and thickness
            ##loc 0 - external, 1- internal
            loc=0
            bound_smooth=0
            restrito=1
            loadtemp=0
            dir_to_save='C:\\Users\\Adriano\\Documents\\VirtualBoxComp\\Mint\\aster\\'
        #    dir_to_save=os.getcwd()+'\\aster\\'
            Jobname=datas.split('.txt')[0]
            curve_default=os.getcwd()+'/curves/'+'CurveX80_py.cf'
            curve=curve_default
    #        print((pipe_input,d_or_r,L,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save))
            rg.aster_rbp(pipe_input,d_or_r,L,thicks,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save,clusterrun)
            
            
def reliabilty_gen(filename):
    def StD_func(acc_rel_abs,conf,insp_type,t):
        if insp_type:
            #StD for UT
            acc_abs = [0.25,0.5,1.]
            StD=np.sqrt(2)*acc_abs[acc_rel_abs]/(t*norm.ppf(0.5+conf/2))
        else:
            #StD for MFL
            acc_rel = [0.05*t,0.1*t,0.2*t]
            StD=acc_rel[acc_rel_abs]/(norm.ppf(0.5+conf/2))
        return StD
    clusterrun=1 # if will run on cluster set to 1
    t=[14.56, #0391
       12.58, #1373
       8.22, #3601
       6.27, #5882
       6.51, #6515
       6.51, #6598
       6.55, #7075
       6.45, #7312
       6.33, #7528
       6.63, #7613
       6.45, #8449
       6.39, #9436
       6.55] #rbp1
    
    def thick(fname):
        thickness={'0391':t[0],
        '1373':t[1],
        '3601':t[2],
        '5882':t[3],
        '6515':t[4],
        '6598':t[5],
        '7075':t[6],
        '7312':t[7],
        '7528':t[8],
        '7613':t[9],
        '8449':t[10],
        '9436':t[11],
        'rbp1':t[12]}
        return thickness.get(fname,'Invalid name')
    file=[]
    file.append(filename)
    
    #################################
    # In[]

    d_or_r=1 #0 - input diameters, 1 - input radius and thickness
    ##loc 0 - external, 1- internal
    loc=0
    bound_smooth=0
    #restrito=1 #casos rodados ate 07/2021
    restrito=1
    loadtemp=0
    D=304.8*2/1000 #mm
    f_u=651.5250 #API5LX80 
    sigu=f_u
    sige=498.276022 #API5LX80
    E=210e3
    Jobname=filename.split('.txt')[0]
    directory = 'adjust_dist'
    data = pd.Series(np.loadtxt(directory+'/'+file[0],delimiter='\t')[:,1])
    longcoord=pd.Series(np.loadtxt(directory+'/'+file[0],delimiter='\t')[:,0])
    thicks=[list(longcoord.copy()/1000),list(data.copy()/1000)]
    L=(np.asarray(longcoord)[-1]-np.asarray(longcoord)[0])/1000
    tn=thick(file[0].split('km.txt')[0])/1000
    # In[Confiability]
    #MFL=0, UT=1
    insp_type=1
    #Accuracy, relative=MFL, absolute=UT - position from list - 0,1,2...
    acc_rel_abs=0
    #Safety class Low=0,Normal=1,High=2 
    safety_class=0
    #Confidence Level
    conf=0.9
    mean=0
    sigma=StD_func(acc_rel_abs,conf,insp_type,tn)
    N=int(1) #number of analysis
    mD = D  ;sD = mD*.03 ; #tD='norm';#m Diâmetro
    mt = tn  ;st = mt*.05 ; #tt='lognorm';#m espessura nominal
    mL = L  ;sL = mL*.05 ; #tL='norm';#m Comprimento do defeito
    md = 0  ;sd = sigma  ; #td='norm';# Profundidade do defeito
    #mPd = 1.05*Pd  ;sPd = mPd*.03 ; tPd='gumbel';#Pa Pressão de Projeto
    mSy = sige  ;sSy = mSy*.056 ; #tSy='lognorm';#MPa Tensão de escoamento
    mSu = sigu  ;sSu = mSu*.03 ; #tSu='norm';#MPa tensão última
    def logn_p(m,s): #calcula os parâmetros para uma lognormal
        mu = np.log((m**2)/(s**2+m**2)**.5);
        sigma = (np.log(s**2/(m**2)+1))**.5;
        return [mu,sigma]
    
    #################################
    deltal_rand=np.random.randn(N)*sL*L/len(thicks[:][0])
    D_rand=np.random.normal(loc=mD,scale=sD,size=N)
    param_t_rand=logn_p(mt,st)
    t_rand=np.random.lognormal(mean=param_t_rand[0],sigma=param_t_rand[1],size=N)
    param_sy_rand=logn_p(mSy,sSy)
    sy_rand=np.random.lognormal(mean=param_sy_rand[0],sigma=param_sy_rand[1],size=N)
    su_rand=np.random.normal(loc=mSu,scale=sSu,size=N)
    # sigma_rand=np.random.normal(loc=md,scale=sd,size=N)
    # sigma_rand=np.zeros(N)
    sigma_rand=StD_func(acc_rel_abs,conf,insp_type,t_rand*1000)/1000 #funcao StD calcula em mm        

    dirCusave=os.getcwd()+'/curves/'
    defy=.005
    defu=.16
    # print(sy_rand,su_rand,defy,defu,E)
    Ar, n, yo, Stress, Def, Stressi, Defi = curves(sy_rand,su_rand,defy,defu,E,Jobname,dirCusave)
    curve=dirCusave+'Curve'+Jobname+'_py'+'.cf'
    pipe_input=[D_rand[0]/2,t_rand[0]]
    # print(tn)
    # print(t_rand)
    # print(D_rand/2-t_rand)
    #Testar truncar os valores abaixo !!!!
    thicks_corr=thicks[:][1]+np.random.randn(1)*sigma_rand #varying thickness equally
    print(thicks[:][1])
    print(thicks_corr)
    L=L+deltal_rand
    coord_corr=np.asarray(thicks[:][0])+np.asarray(range(len(thicks[:][0])))*deltal_rand[0]    
    thicks=[list(coord_corr),list(thicks_corr)]
#        print(Stressi)
#        print(Defi)
    dir_to_save=os.getcwd()+'/../../../../CodeAster'
    L=2.5*L # Tamanho do modelo
    #print((pipe_input,d_or_r,L,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save))
    
    #print(full_data)
    matprop=[sy_rand[0],su_rand[0],defy,defu,E]
    #savedata={'Thicks':thicks,'Data seed':Jobname,'Pipe input':pipe_input,'Lenght':lenght,'Surface':loc,'Clamped':restrito,'Temp':loadtemp,'Material':matprop}
    #print(savedata)
    #data_samples=pd.DataFrame(savedata,columns=['Thicks','Data seed','Pipe input', 'Lenght','Surface','Clamped','Temp','Material'])  
    #print(data_samples)
    rg.aster_rbp(pipe_input,d_or_r,L,thicks,loc,bound_smooth,restrito,loadtemp,Jobname,curve,dir_to_save,clusterrun)
    return thicks, Jobname, pipe_input, L/2.5, loc, restrito,loadtemp,matprop


# thicks=[]
# Jobname=[]
# pipe_input=[]
# lenght=[]
# loc=[]
# restrito=[]
# loadtemp=[]
# matprop=[]
# #reliabilty_gen('7613km.txt')
# for i in range(1):
#     [a, b, c, d, e,f,g,h]=reliabilty_gen('7613km.txt')
#     thicks.append(a)
#     Jobname.append(b)
#     pipe_input.append(c)
#     lenght.append(d)
#     loc.append(e)
#     restrito.append(f)
#     matprop.append(g)
#
# savedata={'Thicks':thicks,'Data seed':Jobname,'Pipe input':pipe_input,'Lenght':lenght,'Surface':loc,'Clamped':restrito,'Temp':loadtemp,'Material':matprop}
#     #print(savedata)

#data_samples=pd.DataFrame(savedata,columns=['Thicks','Data seed','Pipe input', 'Lenght','Surface','Clamped','Temp','Material'])  

#data_samples=pd.DataFrame.from_dict(savedata,orient='index')
#data_samples=data_samples.transpose()

#data_samples=pd.DataFrame(savedata,columns=['Thicks','Data seed','Pipe input', 'Lenght','Surface','Clamped','Temp','Material'])  
#np.savetxt(r'reliability_samples.txt', data_samples.values, fmt='%d')

#samplesfile=os.getcwd()+'/reliability_samples.pkl'
#data_samples.to_pickle(samplesfile)

gen_simplecase()