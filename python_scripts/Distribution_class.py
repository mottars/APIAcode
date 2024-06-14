# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 15:55:20 2018

@author: Adriano
"""
# input:M,    S,   T
#       Mean, STD, Type
# output: P (pdf parameters)

from scipy import stats
import scipy as sp
pi = 3.14159
gamma = 0.5772 #contante de euler:  
def pdf_parameters(M,S,T):
    return {
      'norm': lambda x,y:[M,S],
      'lognorm': lambda x,y:[sp.exp(logn_p(M,S)[0]),logn_p(M,S)[1]],
      'gamma': lambda x,y:[M**2/S**2,S**2/M],
      'expon': lambda x,y:[M],
      'gumbel': lambda x,y:[M - gamma*(S*(6)**(1/2))/(pi),(S*(6)**(1/2))/(pi)]
      }[T](M,S)
      
def logn_p(m,s):
    mu = sp.log((m**2)/(s**2+m**2)**.5);
    sigma = (sp.log(s**2/(m**2)+1))**.5;
    return mu,sigma

def cdf(RV_type,X,P):
    return {
      'norm': lambda x,y:stats.norm.cdf(X,P[0],P[1]),
      'lognorm': lambda x,y:stats.lognorm.cdf(X/P[0],P[1]),
      'gamma': lambda x,y:stats.gamma.cdf(X/P[1],P[0]),
      'expon': lambda x,y:stats.expon.cdf(X/P[0],P[0]),
      'gumbel': lambda x,y:stats.gumbel_r.cdf(X,P[0],P[1])
    }[RV_type](X,P)
    
    
def pdf(RV_type,X,P):
    return {
      'norm': lambda x,y:stats.norm.pdf(X,P[0],P[1]),
      'lognorm': lambda x,y:stats.lognorm.pdf(X/P[0],P[1])/P[0],
      'gamma': lambda x,y:stats.gamma.pdf(X/P[1],P[0])/P[1],
      'expon': lambda x,y:stats.expon.pdf(X/P[0])/P[0],
      'gumbel': lambda x,y:stats.gumbel_r.pdf(X,P[0],P[1])
    }[RV_type](X,P)