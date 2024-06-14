# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 16:15:04 2023

@author: MottaRS
"""

import pandas as pd
import numpy as np
import os
import sys
from inspection_tools import get_spreadsheet_labels, pre_proc_df
# import PipeMA_System.main_pipe_normas as normas
from PipeMA_System import main_pipe_normas

# MAPS
import folium 
import utm
import geopandas as geopd
import branca.colormap as cm

from inspection_tools import  inspection_match, CGR_Comput, find_clusters, joints_match, plot_seaborns, compare_ERF_ProbF


class Pipetally:
    def __init__(self, file_name, date, OD, surce_dir='',future=False, grid_letter='J', sige = 485, sigu = 565, MAOP = 10):
        self.file_name = file_name
        self.date = date
        self.OD = OD
        self.surce_dir = surce_dir
        self.future = future
        
        self.MAOP = MAOP
        self.sige = sige
        self.sigu = sigu
        
        ######################################
        # Gambiarra Não vem no Pipetally -> UTM
        self.grid_letter=grid_letter
        ######################################
        

    def read(self, i=0,  XY0=[], debugon = False):
        # Inspection.append(struct_data())
        # self.file_name = [spreadsheet_name]
        # self.date = date
        # self.OD = OD
        spreadsheet_name = self.file_name
        
        if (spreadsheet_name==[]):
            print('empty spreadsheet_name given')
            return
        
        try:
            df = pd.read_csv(self.surce_dir+os.sep+spreadsheet_name, sep=';' )
        except:
            df = pd.read_excel(self.surce_dir+os.sep+spreadsheet_name,   )
        
        print(spreadsheet_name)
        print("DF size: ",sys.getsizeof(df))
        # print(df['event / comment'])
        
        Labels = df.columns.values
        col_names, Corrosion_comment = get_spreadsheet_labels(Labels)
        df_Def, i_def, df_joints, i_joints, col_names, df, XY0 = pre_proc_df(df,col_names, Corrosion_comment,XY0)
        
        # Saving csv output
        # i=len(Inspection)
        df_Def.to_csv('./DataFrames/Defect_DF_Insp_' + str(i) + '_' + str(self.date))
        
        # self.df_General = df
        self.df_Def = df_Def
        self.i_def = i_def
        self.df_joints = df_joints
        self.i_joints = i_joints
        if debugon: print("DFjoint size: ",sys.getsizeof(df_joints))
        if debugon: print("DFml size: ",sys.getsizeof(df_Def))
        
        # depth_name, def_len_name , def_w_name,t_name , Y_name , X_name  ,H_name , gridzone_name , tube_num_name , tube_len_name , weld_dist_name , Z_pos_name , circ_pos_name , surf_pos_name , ERF_name , feature_name = col_names 
      
        return XY0, col_names
    
    def add_CGR(self, CGR, CGRp, min_CGR = 0.1, max_CGR = 1.2 , debugon = False):
        self.df_Def['CGR'] = CGR
        self.df_Def['CGRp'] = CGRp
        #############################################

    def Identify_Cluster(self, col_names , debugon = False):
        ##########################################################################
        #cluster
        # mm to m
        D = self.OD/1000
        
        cluster, colony_def = find_clusters(self.df_Def, D)
        
        self.clusters = cluster
        # Insps[-1].df_Def['Clusters'] = colony_def
        
        
        self.df_Def['Cluster defs']= np.nan
        self.df_Def['Cluster #']= np.nan
        
        k=0
        for ic in cluster:
            k=k+1
            idx = self.df_Def.iloc[ic].index
            self.df_Def.loc[idx, 'Cluster #']= k
            self.df_Def.loc[idx, 'Cluster defs']= len(ic)
        
        #############################################
        
    def Future_def(self, insp, CGRp, dt=5, debugon = False):
        ##########################################################################
        ##########################################################################
        #############################################
        # future update
        
        
        i_def = insp.i_def
        df_Def = insp.df_Def
        self.i_def = i_def
        self.df_Def = df_Def.copy()
        
        self.df_Def.d= df_Def.d.values + dt*CGRp*100
        
        
    ##############
    # MAPs
    def plot_map(self, name='', plot_joint=True, plot_defect=True, ERF_min=0.92, ERF_max=1.0, save_m=True):

        if len(name)==0:
            name = self.file_name+'_Map'
            
            
        #https://www.movable-type.co.uk/scripts/latlong-utm-mgrs.html
        #Latitude/Northing: n/a / 7585382.088 m
        #Longitude/Easting: n/a / 710594.426 m        
        linear = cm.LinearColormap(["green", "yellow", "red"], vmin=ERF_min, vmax=ERF_max)
        
        df = self.df_joints
        LL=utm.to_latlon(df.X.to_numpy(),df.Y.to_numpy(),df.gridzone.iloc[0],self.grid_letter)
        LL_mean = np.mean(LL,1)
        m = folium.Map(LL_mean, zoom_starts = 5)
        
        
        if plot_joint:
            
            coordinates = list(zip(*LL))
                
            folium.PolyLine(
                locations=coordinates,
                color="#0047AB",
                weight=5,
                tooltip="Pipeline xxx  and defects ERF>0.93",
            ).add_to(m)
            
        
        
        # LL = utm.to_latlon( df.X.to_numpy() , df.X.to_numpy() , df.gridzone.iloc[0], grid_letter)
        # Latitude = LL[0]
        # Longitude = LL[1]
        
        
        if plot_defect:
        # plot_map('Pipe_joint_Map', joint=true, defect=true)
        ############################################################
        ############################################################
        # Plot Defs in map ##############################################
        ############################################################
            df=self.df_Def
            
            
            LL=utm.to_latlon(df.X.to_numpy(),df.Y.to_numpy(),df.gridzone.iloc[0],self.grid_letter)
            df['Lat'] = LL[0]
            df['Long'] = LL[1]
                
            gdf = geopd.GeoDataFrame(
                df, geometry=geopd.points_from_xy(df.Long, df.Lat), crs="EPSG:4326"
            )
            # ................................... geopandas
            
            
            
            m2 = folium.Map(location=[(gdf.geometry.y).mean(), (gdf.geometry.x).mean()], zoom_start=4)
            folium.GeoJson(gdf, name="GeoData").add_to(m2)
            m2.save('Pipi_Defects2.html')
            print("saved Pipi_Defects 2")
            
            # gdf.plot(ax=ax, color="red")
            # plt.show()
            
            
            for ij in range(len(df)):
                if df.ERF.iloc[ij] > 0.93:
                    # LL=utm.to_latlon(df.X.iloc[ij],df.Y.iloc[ij],22,grid_letter)
                    # folium.Marker(LL, popup = 'ERF = '+str(df.ERF.iloc[ij])+', [' +', '.join(map(str, LL))+']',).add_to(m)
                    folium.CircleMarker(
                        location=[LL[0][ij],LL[1][ij]],
                        colors=df.ERF.iloc[ij],
                        colormap=linear,
                        weight=5,
                        popup = 'ERF = '+str(df.ERF.iloc[ij])+', [' +', '.join(map(str, LL))+']',
                        tooltip='ERF = '+str(df.ERF.iloc[ij]),
                    ).add_to(m)
                
                # folium.Marker(
                #     location=[45, -10],
                #     popup=folium.Popup("Let's try quotes", parse_html=True, max_width=100),
                # ).add_to(m)
            
            
            
            ############################################################
            # https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_marker.html#Use-a-Circle-as-a-Marker
            # folium.GeoJson(
            #     gdf,
            #     name="Subway Stations",
            #     marker=folium.Circle(radius=4, fill_color="orange", fill_opacity=0.4, color="black", weight=1),
            #     tooltip=folium.GeoJsonTooltip(fields=["name", "line", "notes"]),
            #     popup=folium.GeoJsonPopup(fields=["name", "line", "href", "notes"]),
            #     style_function=lambda x: {
            #         "fillColor": colors[x['properties']['service_level']],
            #         "radius": (x['properties']['lines_served'])*30,
            #     },
            #     highlight_function=lambda x: {"fillOpacity": 0.8},
            #     zoom_on_click=True,
            # ).add_to(m)
            ############################################################
            ############################################################
            
        if save_m:
            m.save(name+'.html')
            print("saved Pipi_Defects: "+name)
        
        return m
    
    

##########################################################################

def def_critical_limits(dp,t,D,sige, MAOP):
    # ASME B31g based
    
    a = 2/3*dp
    P0 = 1.1*sige*2*t/D*10 *.72
    
    R = MAOP/P0
    
    #P0 * (1-amin) = MAOP
    #amin = 1 - R = 2/3*dp_max
    dp_max = (1 - R)*3/2 # (%)
    #dp_max-dp
    idx = np.where(dp> dp_max*1.2)
    M1 = R*0
    M1[idx]=R[idx]*a[idx]/(R[idx] - 1 + a[idx])
    Llim = R*np.NaN
    Llim[idx] = np.sqrt((M1[idx]**2 -1)*D*t[idx]/.8)
    
    return dp_max, Llim


#####################################
# MSOP (defect assessment)
#####################################
def comput_MSOP(D,t,dp,L,sige,sigu, unit = 'MPa'):
    # D = Inspection[2].OD/1000
    # t = Inspection[2].df_Def[t_name].values/1000
    # dp = Inspection[2].df_Def[depth_name].values/100
    # L = Inspection[2].df_Def[def_len_name].values/1000
    
    # API 5L X70
    # sige = 485 
    # sigu = 565 
    # MAOP = 100 #bar
    thicks=[]
    # DNV RP F101 d = d+ alph*StDd (example A1)
    # d = (dp+0.21)*t
    d = (dp+0)*t
    
    Ndef = len(d)
    PFs = np.zeros(Ndef)

    for i in range(Ndef):
        PFs[i] = main_pipe_normas.modifiedb31g(D,t[i],L[i],d[i],sige,sigu,thicks)
    
    if (unit.upper()=='BARS')|(unit.upper()=='BAR'):
        MSOP = PFs*10*.72
    elif (unit.upper()=='MPA'):
        MSOP = PFs*.72
    else:
        print('Nao encontrada unidade: ', unit)
    print(MSOP[0])
    return MSOP

##################################################


#############################################
class struct_dataxxxxx:
        pass
    
def read_inspectionXXX(Inspection,pd,spreadsheet_name, OD, date, surce_dir, XY0=[], debugon = False):
    
    Inspection.append(struct_data())
    Inspection[-1].file_name = [spreadsheet_name]
    Inspection[-1].date = date
    Inspection[-1].OD = OD
    
    if (spreadsheet_name==[]):
        return
    
    try:
        df = pd.read_csv(surce_dir+os.sep+spreadsheet_name, sep=';' )
    except:
        df = pd.read_excel(surce_dir+os.sep+spreadsheet_name,   )
    
    print(spreadsheet_name)
    print("DF size: ",sys.getsizeof(df))
    
    Labels = df.columns.values
    col_names, Corrosion_comment = get_spreadsheet_labels(Labels)
    df_Def, i_def, df_joints, i_joints, col_names, df, XY0 = pre_proc_df(df,col_names, Corrosion_comment,XY0)
    
    # Saving csv output
    i=len(Inspection)
    df_Def.to_csv('./DataFrames/Defect_DF_Insp_' + str(i) + '_' + str(Inspection[i-1].date))
    
    # Inspection[-1].df_General = df
    Inspection[-1].df_Def = df_Def
    Inspection[-1].i_def = i_def
    Inspection[-1].df_joints = df_joints
    Inspection[-1].i_joints = i_joints
    if debugon: print("DFjoint size: ",sys.getsizeof(df_joints))
    if debugon: print("DFml size: ",sys.getsizeof(df_Def))
    
    # depth_name, def_len_name , def_w_name,t_name , Y_name , X_name  ,H_name , gridzone_name , tube_num_name , tube_len_name , weld_dist_name , Z_pos_name , circ_pos_name , surf_pos_name , ERF_name , feature_name = col_names 
  
    return XY0, col_names
