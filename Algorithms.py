# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 17:10:13 2022
LCRS
Based on MIT lecture posted @: https://youtu.be/V5hZoJ6uK-s?t=3228);

MRSI by  MottaRS

@author: MottaRS
"""

#


import numpy.linalg as np

def MRSI_3D(A, B,tol=1, debug=False):
    #Monotonic_Real_Sequence_Intersection
    n, m = len(A),len(B)
    if debug: print('MRSI, n,m, tol = ',n,m, tol)
    # print('A = ',A)
    # print('B = ',B)
    # L = np.zeros(m+1)
    # L = [[]]*(m+2)
    # pos = [[]]*(m+2)
    # pos = [[],[]]*m
    posa = [0]*n
    posb = [0]*m
    i_match=0
    pos = []
    ib0=0
    
    # ok=0
    for ia in range(0,n):
        dd = tol
        first_found = False
        # ok=0
        for ib in range(ib0,m):
            if debug: print('ia,ib = ',ia,ib)
            if debug: print('Aia,Bib = ',A[ia],B[ib])
            
            dd_new = np.norm(A[ia] - B[ib])
            if not first_found:
                if dd_new < dd: 
                    #OK 1st foiuund, is min? (keep searching)
                    first_found = True 
                    # ok=1
                    dd = dd_new
                    posi = [ia,ib]
                    # pa=ia
                    # pb=ib
                    
            else:
                if dd_new < dd: 
                    #keep searching min
                    dd=dd_new
                    posi = [ia,ib]
                    # pa=ia
                    # pb=ib
                else:
                    # Finished: get previously results (posi)
                    pos.append(posi)
                    i_match+=1
                    posa[posi[0]] = i_match
                    posb[posi[1]] = i_match
                    ib0 = posi[1]
                    break 
                
    return pos, posa, posb

def MRSI(A, B,tol, debug=False):
    #Monotonic_Real_Sequence_Intersection
    n, m = len(A),len(B)
    if debug: print('MRSI, n,m, tol = ',n,m, tol)
    # print('A = ',A)
    # print('B = ',B)
    # L = np.zeros(m+1)
    # L = [[]]*(m+2)
    # pos = [[]]*(m+2)
    # pos = [[],[]]*m
    posa = [0]*n
    posb = [0]*m
    i_match=0
    pos = []
    ib0=0
    ok=0
    for ia in range(0,n):
        dd = tol
        first_found = False
        ok=0
        for ib in range(ib0,m):
            if debug: print('ia,ib = ',ia,ib)
            if debug: print('Aia,Bib = ',A[ia],B[ib])
            
            if first_found:
                dd_new = abs(A[ia] - B[ib])
                if dd_new < dd: 
                    #keep searching min
                    dd=dd_new
                    posi = [ia,ib]
                    pa=ia
                    pb=ib
                else:
                    pos.append(posi)
                    i_match+=1
                    posa[ia] = i_match
                    posb[ib] = i_match
                    ib0 = ib
                    break 
                
            if abs(A[ia] - B[ib]) < dd: 
                #OK 1st foiuund, is min? (keep searching)
                first_found = True 
                ok=1
                dd = abs(A[ia] - B[ib])
                posi = [ia,ib]
                pa=ia
                pb=ib
                
    return pos, posa, posb

def LCRS_linear(A, B,tol):
    n, m = len(A),len(B)
    print('LCRS_linear, n,m = ',n,m)
    # L = np.zeros(m+1)
    L = [[]]*(m+2)
    pos = [[]]*(m+2)
    # for ia = n ;ia >=0; ia - -) 
    for ia in range(n,-1,-1): 
        
        k1 =[]
        posj=[]
        # for ( ib = m ;ib >=0; ib - -) :
        for ib in range(m,-1,-1):
            # a=range(3,0,-1)
            print('ia,ib = ',ia,ib)
            if ia==n or  ib==m : 
                k2 = []
                posi=[]
                print(1,k2)
            elif abs(A[ia] - B[ib])<=tol: 
                print('B[ib] , A[ia] = ',B[ib] , A[ia])
                k2 =  [A[ia]]+ L[ib+1]
                posi = [ia,ib]
                print('2,k2=',k2)
            else:
                print('L[ib],len(k1)',L[ib],(k1))
                n1,n2=len(L[ib]),len(k1)
                print('n1,n2=',n1,n2)
                # posi=[]
                if n1>n2:
                    k2 = L[ib]
                    # posi = []
                else:
                    k2 = k1
                    posi = posj
                print(3,k2)
            print('posi = ',posi)
            
            pos[ib+1]=posi + pos[ib+1]
            print('poss = ',pos)
            L[ib+1]=k1
            k1 = k2 
            print('posij = ',posi)
            posj=posi
            
            print(4,k2)
            
        pos[0]=posj #+ pos[ib+1]
        L[0]=k1
        print('Ltot = ',L)
        print('pos_tot = ',pos)
    
    return L [0], pos[0]


# Longest Common Real Subsequence
# input: 
#    A, B = sequence of real numbers
#    tol
def LCRS_mit(A, B,tol):
    debug = False
    # debug = True
    N, M = len(A),len(B)
    pos=[]
    delt=[]
    if N <= 0 or M <= 0:
        return []
    res_matrix = [[None] * M for i in range(N)]
    pos = [[None] * M for i in range(N)]
    delt = [[None] * M for i in range(N)]

    def lcrs(i, j):
        if i <= -1 or j <= -1:
            return [], [], []
        if debug: print(i,j,res_matrix[i][j])
        if res_matrix[i][j] == None:
            if debug: print(A[i], B[j], '?')
            if abs(A[i] - B[j])<tol:
                a,posi,delti = lcrs(i - 1, j - 1)
                if debug: print('tudo ', a,posi,delti, res_matrix[i][j] )
                res_matrix[i][j] = a + [(A[i] + B[j])/2]
                if debug: print('saio ok ', res_matrix)
                
                pos[i][j] = posi + [[i,j]]
                delt[i][j] = delti + [(A[i] - B[j])]
                
                #res_matrix[i][j] = lcrs(i - 1, j - 1) + [(A[i] + B[j])/2]
                # delt.append(A[i] - B[j])
                # pos.append([i,j])
                if debug: print('saio ok ', pos)
                if debug: print('saio ok ', delt)
                
            else:
                if debug: print('prev1')
                prev1,pos1,delt1 = lcrs(i - 1, j)
                if debug: print('prev2')
                prev2,pos2,delt2 = lcrs(i, j - 1)
                if debug: print('previs: ',prev1,prev2)
                n1,n2 = len(prev1),len(prev2)
                
                if (n1>n2): 
                    res_matrix[i][j] = prev1 
                    pos[i][j] = pos1 #+ [i-,j]
                    delt[i][j] = delt1 #+ [(A[i] - B[j])]
                    if debug: print('1')
                else:
                    res_matrix[i][j] = prev2
                    pos[i][j] = pos2 #+ [i,j]
                    delt[i][j] = delt2 #+ [(A[i] - B[j])]
                    if debug: print('2')
                    
                # pos.append([-i,-j])
                
                if debug: print('saio 2')
            if debug: print(res_matrix[i][j])
        if debug: print('i,j: ',i,j)
        if debug: print('pos: ',pos)
        if debug: print('res_matrix: ',res_matrix)
        if debug: print('out: ',res_matrix[i][j])
        return res_matrix[i][j], pos[i][j], delt[i][j]
    
    return lcrs(N - 1, M - 1)

def main():
    
    import numpy as np
    import matplotlib.pyplot as plt
    
    # A=np.array([0,3,12.13,0,124.,340.1,555.01, 666, 700+range(20)])
    A=np.concatenate((np.array([7,8,0,3,12.09,0,124.,340.1,555.01, 666,7,8,9,12]), 700+np.arange(2)))
    B=np.concatenate((np.array([1.5,7,8,9,12.0,12.12,13,124.09,222,340.03,555,666]), 700+np.arange(3)))
    
    # A=[2,3,2]
    # B=[1,2,3]
    tol = .1
    
    # aa, posa, delt = LCRS_mit(A, B,tol)
    posa, pa, pb= MRSI(A, B,tol)
    print('pa',pa)
    print('pb',pb)
    print(posa)
    Ae = np.array([A[il[0]] for il in posa])
    Be = np.array([B[il[1]] for il in posa])
    
    
    print('tolerance = ',tol)
    print('Input A = ',A)
    print('Input B = ',B)        
    print('Ae : ',Ae)
    print('Be : ',Be)
    print('Difereces (<tol) : ', Ae-Be)
    # print('Delt (<tol) : ',delt)
    print('Positions [A,B] : ',posa)
    print('diff(pos) = ',np.diff(posa).transpose())
    plt.hist(np.diff(posa))
    
if __name__ == "__main__":
    print('mailn')
    main()
