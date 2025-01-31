# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 12:50:31 2017

@author: Adriano
"""
import scipy as sp
import numpy as np
from numpy import sign, isfinite
from scipy import stats
import python_scripts.Distribution_class as DC
#from G_calc import G_calc
# from Sistema_Cordut.main_pipe_normas import effective_area as effecArea

########### FORM ############ 
def FORM(M,RV_type,P,fun_G,*args):
    
    max_iter = 50
    # ponto inicial
    # X=np.transpose(M)
    X=np.array(M)
    dx = X*1e-5 #diferencas finitas
    Xr=X*0
    nRV = len(X)
    #G=G_calc(fun_G,Param,X,L)
    #G=G_calc(fun_G,X)-X[4]
    # G=effecArea(X[0],thicks,X[1],StDtd,X[5],StDtd,X[2])-X[3]
    G=fun_G(X,*args)
    #G=effective_area(X[0],X[1],X[2],StDtd,X[4],thicks)-X[3]
    #G=b31g(X[0],X[1],X[2],min(thicks[:,1]),X[4])-X[3]
    # print('G_0 = '+str(G))
    Seq=np.zeros(nRV)
    Meq=np.zeros(nRV)
    dGdx=np.zeros(nRV)
    # G_step=2*G
#    while abs(1-G/G_step)>1e-3:
    ii=0
    beta=0
    #while abs(G)>1e-3 or ii<1e2:
    # print('beta = %.6f'%0+', G = %.10f'%G+', iter = %.0f'%ii)
    G0=G
    desv=1
    # while abs(G/G0)>1e-6:
    while (desv>1e-3) | (abs(G/G0)>1e-5):
        ii=ii+1
        #G_step=G
        # Normal Equivalent Distribution
        for i in range(nRV):
            #print(RV_type[i],X[i],P[i][:])
            Px=DC.cdf(RV_type[i],X[i],P[i][:])
            px=DC.pdf(RV_type[i],X[i],P[i][:])
            if px<1e-25:
                px = 1e-25
            if Px<1e-25:
                Px = 1e-25
            Xr[i]=stats.norm.ppf(Px,0,1)
            Seq[i]=stats.norm.pdf(Xr[i])/px
            Meq[i]=X[i]-Xr[i]*Seq[i]
        
        Xr[Xr>1e15]=1e15
        # Comput Gradient
        #[G1,dGdx]=feval(fun_G,X,f_par{:});
        # Finite Difference (dGdx)
        for i in range(nRV):
            X[i] = X[i] + dx[i]
            
            # Compute Failure Function
            G1=fun_G(X,*args)

            dGdx[i] = (G1 - G)/dx[i]
            X[i]=X[i]-dx[i]

        # print('dGdX')
        # print(dGdx)
        
        # Jacobian Transformation, J = sp.diag(Seq);
        dGr = Seq*dGdx
        L = sp.linalg.norm(dGr)
        
        alpha = dGr/L
        # print('Xr')
        # print(Xr)
        # print(alpha)
        if ~isfinite(beta):
            break
        desv = sp.linalg.norm(alpha*beta + Xr)

        # print(desv)
        
        beta = G/L - Xr.dot(alpha)
        Xr = -beta*alpha
        # print("Xr")
        # print(Xr)
        X = np.transpose(Xr)*Seq+Meq
        
        G=fun_G(X,*args)
        
        # print('beta = %.6f'%beta+', G = %.10f'%G+', iter = %.0f'%ii)
        # print('X')
        # print(X)
        if ii>max_iter:
            break
        if ~isfinite(beta):
            break
        if ~isfinite(G):
            beta=np.nan
            break
        
    MPP = X;
    # beta=sp.linalg.norm(Xr)*sign(G0)
    # if sign(G0)==-1:
    print('beta = %.6f'%beta+', G = %.10f'%(G/G0)+', iter = %.0f'%ii)
    PF_form=DC.cdf('norm',-beta,[0,1])
    # print('PF_form = %.19f'%PF_form+'\n')

    
    # MPP_sobre_M = MPP/M
    # [mdif,km]=[MPP_sobre_M[sp.argmax(MPP_sobre_M)],sp.argmax(MPP_sobre_M)];
    # print('Mdif = %.6f'%mdif+'\n')
    return PF_form, beta, MPP, ii, alpha
