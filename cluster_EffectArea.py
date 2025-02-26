# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 22:18:31 2025

@author: MottaRS

function to obtain the RBP from clusters of idealized defects

"""
import matplotlib.pyplot as plt
# from numpy import array as narray
import numpy  as np


def compute_depth_profile(intervals, depths):
    # Extract all unique critical points and sort them
    points = sorted({point for interval in intervals for point in interval})
    
    # Create segments between consecutive points
    segments = []
    for i in range(len(points) - 1):
        start, end = points[i], points[i+1]
        max_depth = 0.0
        
        # Check all intervals for overlap with current segment
        for (s, e), depth in zip(intervals, depths):
            if s < end and e > start:  # Check for overlap
                max_depth = max(max_depth, depth)
                
        segments.append((start, end, max_depth))
    
    # Merge consecutive segments with the same depth
    if not segments:
        return []
    
    merged = [segments[0]]
    for seg in segments[1:]:
        last_start, last_end, last_depth = merged[-1]
        current_start, current_end, current_depth = seg
        
        if current_start == last_end and current_depth == last_depth:
            # Merge segments
            merged[-1] = (last_start, current_end, last_depth)
        else:
            merged.append(seg)
    
    position = [merged[0][0]]
    ds=[0]
    for start, end, depth in merged:
        position.append(start)
        position.append(end)
        ds.append(depth)
        ds.append(depth)
    position.append(end)
    ds.append(0)
    
    return position, ds

def plot_defects(positions, depths):
    """
    Plot the defect profile with depth transitions at interval boundaries.
    """
        
    # Sort for plotting
    # order = np.argsort(positions)
    # positions = np.array(positions)[order]
    # depths = np.array(depths)[order]
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(positions, 1-np.array(depths), 'b-', linewidth=2, label="Defect Profile")
    plt.fill_between(positions, 1-np.array(depths), color='lightblue', alpha=0.5)
    
    plt.xlabel("Position")
    plt.ylabel("Depth")
    plt.title("Defect Depth Profile")
    plt.grid(True)
    plt.legend()
    plt.show()
    
# In[main]
if __name__ == '__main__':
    ###################################################
    # Example usage
    xx = [[1, 3], [4, 6], [5, 12], [7, 9], [11, 13]]
    dd = [0.4, 0.2, 0.4, 0.3, 0.1]
    
        
    # xx =  [[0.017500000000005796, 0.0385000000000058], [0.08399999999999898, 0.11199999999999898],
    #        [0.12350000000000011, 0.13250000000000012], [0.18849999999999795, 0.20349999999999796], 
    #        [0.23000000000000442, 0.25400000000000444], [0.24750000000000022, 0.26450000000000023]]
    # dd = [0.1,  0.1 , 0.22, 0.21, 0.14, 0.1 ]
    positions, ds = compute_depth_profile(xx, dd)
    # Print the result
    # plt.plot([0,0.3,0.3,0],[0,0,1,1])
    # plt.plot(positions,depth )
    plot_defects(positions, ds)

def create_intervals(cluster_details):
    Ls = cluster_details.L[0]/1000
    # ts = cluster_details.t[0]
    ds = cluster_details.d[0]/100
    Zs = cluster_details.Z[0]
    Zs = Zs - (np.min(Zs) - np.max(Ls))
    x0 = Zs - Ls/2
    x1 = Zs + Ls/2
    
    xx=[]
    for k in range(len(x0)):
        xx.append([x0[k], x1[k]])
    
    # print('xx, ds = ',xx, ds)
    positions, depths = compute_depth_profile(xx,ds)
    
    return positions, depths
        