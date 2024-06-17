# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 16:15:04 2023

@author: MottaRS
"""

import pandas as pd
import numpy as np
import os
import sys
from inspection_tools import get_spreadsheet_labels, pre_proc_df, find_clusters

# MAPS
import folium 
import utm
import geopandas as geopd
import branca.colormap as cm

   


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
        # df_Def.to_csv('./DataFrames/Defect_DF_Insp_' + str(i) + '_' + str(self.date))
        
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
        
    def Future_def(self, dt=5, debugon = False):
        ##########################################################################
        ##########################################################################
        # future update
        
        self.future = True
        self.df_Fut_Def = self.df_Def.copy()
        self.df_Fut_Def.d= self.df_Def.d.values + self.df_Def.CGRp*dt
        
        #############################################
        
    ##############
    # MAPs
    def plot_map(self, name='', plot_joint=True, plot_defect=True, ERF_min=0.8, ERF_max=1.0, save_m=True):

        if len(name)==0:
            name = self.file_name+'_Map'
            
            
        #https://www.movable-type.co.uk/scripts/latlong-utm-mgrs.html
        #Latitude/Northing: n/a / 7585382.088 m
        #Longitude/Easting: n/a / 710594.426 m
        df = self.df_joints.copy()
        ## utm.to_latlon() function may change the Y value, use df = self.df_joints.copy() instead
        LL=utm.to_latlon(df.X.to_numpy(),df.Y.to_numpy(),df.gridzone.iloc[0],self.grid_letter)  
        LL_mean = np.mean(LL,1)
        m = folium.Map(LL_mean, zoom_starts = 5)
        
        if plot_joint:
            
            coordinates = list(zip(*LL))
            
            folium.PolyLine(
                locations=coordinates,
                color="slategray",
                weight=5,
                tooltip="Pipeline xxx  and defects ERF>0.93",
            ).add_to(m)
        
        # LL = utm.to_latlon( df.X.to_numpy() , df.X.to_numpy() , df.gridzone.iloc[0], grid_letter)
        # Latitude = LL[0]
        # Longitude = LL[1]
        
        
        if plot_defect:
        # plot_map('Pipe_joint_Map', joint=true, defect=true)
        ############################################################
        # Plot Defs in map ##############################################
        ############################################################
            df=self.df_Def.copy()
            
            LL=utm.to_latlon(df.X.to_numpy(),df.Y.to_numpy(),df.gridzone.iloc[0],self.grid_letter)

            ############################################################
            # ................................... geopandas
            df['Lat'] = LL[0]
            df['Long'] = LL[1]
            gdf = geopd.GeoDataFrame(
                df, geometry=geopd.points_from_xy(df.Long, df.Lat), crs="EPSG:4326"
            )
            # gdf.ERF.fillna(0.0)
            # gdf=gfd.assign('radius' = ['d'])
            # gdf=gfd.assign('radius' = ['d'])
            
            # ERFmin = gdf['ERF'].min()
            colormap= cm.LinearColormap(["blue", "green", "yellow", "red", "darkred"], vmin=ERF_min, vmax=1.0,
                                        caption="ERF")
            gdf['ERF']=gdf['ERF'].fillna(0)
            gdf['color'] = gdf['ERF'].fillna(0).apply(colormap)
            gdf['radii'] = gdf['d']/5+20 #(gdf['L']**.5)
            # m = folium.Map(location=[(gdf.geometry.y).mean(), (gdf.geometry.x).mean()], zoom_start=4)
            folium.GeoJson(gdf, 
                           marker=folium.Circle(radius=4, fill_color="orange", fill_opacity=0.2, color="black", weight=1),
                           tooltip=folium.GeoJsonTooltip(fields=["feature", "ERF", "Lat","Long"]),
                           style_function=lambda x: {
                                    "fillColor": x['properties']['color'],
                                    "radius": x['properties']['radii'],
                                    "fillOpacity": x['properties']['ERF'],
                                },
                           highlight_function=0.3, #lambda x: {"fillOpacity": x['properties']['ERF']},
                           zoom_on_click=True,

                           name="Defects GeoData"
                           ).add_to(m)
            
            # icon=folium.DivIcon(html=f"""<div style="font-family: Verdana; color: collors>{"{:.0f}".format(temp)}</div>""")
            for lat, lon, value, color in zip(gdf['Lat'],gdf['Long'],gdf['ERF'],gdf['color']):
                folium.Marker(location=[lat,lon],
                              icon=folium.DivIcon(html=f"""<div style="font-family: Tahoma ; font-size: 1.5em; color: {color};"><-{value:.2f}</div>""")
                              ).add_to(m)
            
            
            
            colormap.add_to(m)
            
            # https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_marker.html#Use-a-Circle-as-a-Marker
            # folium.GeoJson(
            #     gdf,
                    
            
            
        if save_m:
            m.save(name+'.html')
            print("saved Pipi_Defects: "+name)
        
        return m
    
    

##########################################################################



#############################################
# TRASH!
# class struct_dataxxxxx:
#         pass
    
# def read_inspectionXXX(Inspection,pd,spreadsheet_name, OD, date, surce_dir, XY0=[], debugon = False):
    
#     Inspection.append(struct_data())
#     Inspection[-1].file_name = [spreadsheet_name]
#     Inspection[-1].date = date
#     Inspection[-1].OD = OD
    
#     if (spreadsheet_name==[]):
#         return
    
#     try:
#         df = pd.read_csv(surce_dir+os.sep+spreadsheet_name, sep=';' )
#     except:
#         df = pd.read_excel(surce_dir+os.sep+spreadsheet_name,   )
    
#     print(spreadsheet_name)
#     print("DF size: ",sys.getsizeof(df))
    
#     Labels = df.columns.values
#     col_names, Corrosion_comment = get_spreadsheet_labels(Labels)
#     df_Def, i_def, df_joints, i_joints, col_names, df, XY0 = pre_proc_df(df,col_names, Corrosion_comment,XY0)
    
#     # Saving csv output
#     # i=len(Inspection)
#     # df_Def.to_csv('./DataFrames/Defect_DF_Insp_' + str(i) + '_' + str(Inspection[i-1].date))
    
#     # Inspection[-1].df_General = df
#     Inspection[-1].df_Def = df_Def
#     Inspection[-1].i_def = i_def
#     Inspection[-1].df_joints = df_joints
#     Inspection[-1].i_joints = i_joints
#     if debugon: print("DFjoint size: ",sys.getsizeof(df_joints))
#     if debugon: print("DFml size: ",sys.getsizeof(df_Def))
    
#     # depth_name, def_len_name , def_w_name,t_name , Y_name , X_name  ,H_name , gridzone_name , tube_num_name , tube_len_name , weld_dist_name , Z_pos_name , circ_pos_name , surf_pos_name , ERF_name , feature_name = col_names 
  
#     return XY0, col_names
