# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 16:29:15 2020
Rbp idle functions 
@author: Adriano
"""
# import sys,os
#sys.path.insert(1, 'C:/Users/Adriano/Google Drive/UFPE/Carreira.Acadêmica/Doutorado/code_aster_dutos')
import numpy as np
from python_scripts.read_file import read_txt_file

def rbp_from_3d(directory,file):
    thickness = read_txt_file(directory+'\\'+file)   
    #thickness = read_txt_file("Real_Ideal_def_tab.txt")
    #aShape = constrained_filling()
    yi = thickness[1:,0]
    # xi = thickness[0,1:]
    zi = thickness[1:,1:]
    # print('yi T=',yi)
    # print('xi T=',xi)
    # print('zi T=',zi)
    # print('miniT=',thickness[0:6,0:8])
    rbpi=np.amin(zi,axis=1)
    print('Min T=', min(rbpi))
    print('Ave T=', np.mean(zi))
    rpb_m=[]
    for i,j in zip(rbpi,yi):
        rpb_m.append([j,i])
    rpb_m=np.asarray(rpb_m)
    # print('rpb_m =', rpb_m)
    return rpb_m
