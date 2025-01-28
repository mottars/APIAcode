# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 18:42:01 2025

@author: MottaRS
"""


def inverse_modifiedb31g(D, t, L, sige, sigu, pf, thicks=0):
    # Calculate sflow based on sige
    if sige <= 483:
        sflow = sige + 69
    else:
        sflow = sige * 1.1
    
    # Calculate P0
    P0 = sflow * ((2 * t) / D)
    
    # Calculate z
    z = L**2 / (D * t)
    
    # Calculate M based on z
    if z > 50:
        M = 0.032 * z + 3.3
    else:
        M = (1 + 0.6275 * z - 0.003375 * (z**2))**0.5
    
    # Rearrange the equation to solve for d
    # pf = P0 * ((1 - Q) / (1 - (Q / M)))
    # Q = 0.85 * d / t
    # Let's solve for Q first:
    # pf / P0 = (1 - Q) / (1 - (Q / M))
    # Let's denote A = pf / P0
    A = pf / P0
    
    # Now, solve for Q:
    # A = (1 - Q) / (1 - (Q / M))
    # A * (1 - (Q / M)) = 1 - Q
    # A - A*(Q / M) = 1 - Q
    # A - 1 = A*(Q / M) - Q
    # A - 1 = Q*(A / M - 1)
    # Q = (A - 1) / (A / M - 1)
    
    Q = (A - 1) / (A / M - 1)
    
    # Now, solve for d:
    # Q = 0.85 * d / t
    d = (Q * t) / 0.85
    
    return d

def modifiedb31g(D,t,L,d,sige,sigu,thicks=0):
    # 085dL ASME B31g (2009)
    if sige<=483:
        sflow = sige+69
    else:
        sflow = sige*1.1
    P0 = sflow*((2*t)/D)
    if(D and t and L and d and sige):
        z = L**2/(D*t)
        if (z>50):
            M=0.032*z+3.3
            # pf=sflow*((2*t)/D)*(1-d/t)
        else:
            M=(1+.6275*z-0.003375*(z**2))**0.5
        Q = 0.85*d/t
        pf=P0*((1-Q)/(1-(Q/M)))
    return pf

D = 36  # Diameter
t = 0.5  # Wall thickness
L = 10  # Length of the defect
sige = 400  # Yield strength
sigu = 500  # Ultimate strength
pf = 1000  # Failure pressure

d = inverse_modifiedb31g(D, t, L, sige, sigu, pf)
print(f"The defect depth d is: {d}")