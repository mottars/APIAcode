# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 16:15:04 2023

@author: MottaRS
"""

import pandas as pd
import numpy as np
import os
import sys
import inspection_tools as itools

# get_spreadsheet_labels, pre_proc_df, find_clusters, comput_MSOP, def_critical_limits

from python_scripts import Risk_Module as risk
from python_scripts import main_pipe_normas as sempiric

# MAPS
import folium 
import utm
import geopandas as geopd
import branca.colormap as cm


class Inspection_data:
    def __init__(self, file_name, date, OD, surce_dir='',future=False, grid_letter='J', sige = 485, sigu = 565, MAOP = 10, Insp_type = 'MFL',Confid_level=0.85, Accuracy=0.1, acc_rel =-1, F = 0.72):
        self.file_name = file_name
        self.date = date
        self.OD = OD
        self.surce_dir = surce_dir
        self.future = future
        
        self.MAOP = MAOP
        self.sige = sige
        self.sigu = sigu
        self.F = F
        
        # Inspection Tool DATA:
        self.Insp_type=Insp_type ## MFL, UT
        # PIG instrument tolerance
        self.Confid_level = Confid_level
        self.Accuracy = Accuracy
        # Accuracy_rel_abs== MFL
        #   Accuracy = 0.05*t,0.1*t,0.2*t,...
        # Accuracy_rel_abs== UT
        #   Accuracy = 0.25,0.5,1.,...
        
        ######################################
        # Gambiarra Não vem no Pipetally -> using UTM !!!!!!!!!!!
        self.grid_letter=grid_letter
        ######################################
    
    def Tally_read(self, i=0,  XY0=[], debugon = False):
        # Pipe Tally read to Data Frame
        
        spreadsheet_name = self.file_name
        
        if (spreadsheet_name==[]):
            print('empty spreadsheet_name given')
            return
        
        try:
            df = pd.read_csv(self.surce_dir+os.sep+spreadsheet_name, sep=';' )
        except:
            df = pd.read_excel(self.surce_dir+os.sep+spreadsheet_name,   )
        
        print(spreadsheet_name)
        
        if debugon: print("Raw Data Frame size: ",sys.getsizeof(df))
        df=itools.skp_header(df,debugon)
        print("New Raw Data Frame size: ",sys.getsizeof(df))
        if debugon: print("Columns = ",df.columns.values)
        
        Labels = df.columns.values
        col_names, Corrosion_comment = itools.get_spreadsheet_labels(Labels)
        if debugon: print("Columns setted = ",col_names)
        df_Def, i_def, df_joints, i_joints, col_names, df, XY0 = itools.pre_proc_df(df,col_names, Corrosion_comment,XY0)
        
        
        # self.df_General = df
        self.df_Def = df_Def
        self.i_def = i_def
        self.df_joints = df_joints
        self.i_joints = i_joints
        self.t0 = np.min(df_joints.t.values)
        if debugon: print("DFjoint size: ",sys.getsizeof(df_joints))
        if debugon: print("DFml size: ",sys.getsizeof(df_Def))
        
        # depth_name, def_len_name , def_w_name,t_name , Y_name , X_name  ,H_name , gridzone_name , tube_num_name , tube_len_name , weld_dist_name , Z_pos_name , circ_pos_name , surf_pos_name , ERF_name , feature_name = col_names 
        
        return XY0, col_names
    
    def barlow_eq(self):
        
        i=self
        
        self.barlow_pressure = i.sige*((2*i.t0)/i.OD)*i.F
        self.ERF_base = i.MAOP/self.barlow_pressure 
        

    def add_CGR(self, CGR, CGRp, min_CGR = 0.1, max_CGR = 1.2 , debugon = False):
        self.df_Def['CGR'] = CGR
        self.df_Def['CGRp'] = CGRp
        #############################################

    def Identify_Cluster(self, col_names , debugon = False):
        ##########################################################################
        #cluster
        # mm to m
        D = self.OD/1000

        cluster, colony_def, cluster_size = itools.find_clusters(self.df_Def, D, debugon)
        self.clusters = cluster
        # Insps[-1].df_Def['Clusters'] = colony_def
        
        
        self.df_Def['Cluster defs']= np.nan
        self.df_Def['Cluster #']= 0
        df_cluster = pd.DataFrame(columns=['d', 'L', 'w', 't', 'Z_pos', 'clock_pos', 'Cluster #', 'Cluster defects'])
        k=-1
        cluster_list = []
        for ic in cluster:
            k=k+1
            idx = self.df_Def.iloc[ic].index
            self.df_Def.loc[idx, 'Cluster #']= k+1
            self.df_Def.loc[idx, 'Cluster defs']= len(ic)
            clstr_d = np.max(self.df_Def.iloc[ic].d)
            clstr_t = np.mean(self.df_Def.iloc[ic].t)
            try:
                new_rows = {'defs': idx, 'd': clstr_d, 'L': cluster_size[k][0], 'W': cluster_size[k][1], 't': clstr_t, 'Z_pos': cluster_size[k][2], 'clock_pos': cluster_size[k][3], 'Cluster #': k+1, 'Cluster defects': len(ic)}
            except:
                print(k, len(cluster), len(cluster_size), clstr_d,  cluster_size[k-1])
            
            cluster_list.append(new_rows)
            
        # df_cluster = self.df_Def.loc[self.df_Def['Cluster #'] != 0]
        # Append all rows at once
        # print(k, len(cluster), len(cluster_size), clstr_d,  cluster_size[k-1])
        df_cluster = pd.concat([df_cluster, pd.DataFrame(cluster_list)], ignore_index=True)
        self.df_cluster = df_cluster 
        #############################################
        
    def Future_def(self, Dates, dt, debugon = False):
        ##########################################################################
        ##########################################################################
        # future update
        self.future = True
        self.date = Dates
        self.file_name = self.file_name+'_Future'
        self.date.append(Dates[-1]+dt)
        self.df_Def.d= self.df_Def.d.values + self.df_Def.CGRp*dt
        
        #############################################
    def get_pipe_data(self):
        
        D  = self.OD/1000
        # t  = self.t0/1000
        sige = self.sige
        sigu = self.sigu
        F = self.F
        MAOP = self.MAOP
        
        return D,sige,sigu,F, MAOP
    
    
    def Defects_Analysis(self, analysis_type = sempiric.modifiedb31g, def_type = 'single', cluster_details=[]):
                

        MAOP = self.MAOP
        
        # pipe_data = Inspection_data.get_pipe_data(self)
        [D,sige,sigu,F, MAOP] = self.get_pipe_data()
        
        # Meters
        # D  = self.OD/1000
        Ls  = self.df_Def.L.values/1000
        ts  = self.df_Def.t.values/1000
        
        dp = self.df_Def.d.values/100 # dp(%)
        # d  = dp*t
        
        if (def_type.lower()=='single'):
            MSOP = itools.comput_MSOP(D,sige,sigu,F,ts,dp,Ls, unit = 'MPa', method=analysis_type)
            
            self.df_Def['MSOP'] = MSOP
            self.df_Def['ERF'] = MAOP/MSOP
            
            # print('VER -> itools.def_critical_limits(dp,t,D,sige, MAOP)')
            [d_max, Llim] = sempiric.inverse_modifiedb31g(D, sige, sigu, ts, Ls, dp*ts, MAOP/F)
            
            self.df_Def['L max'] = Llim*1000
            self.df_Def['Max Safety d [%]'] = d_max/ts*100
            
        elif (def_type.lower()=='cluster'):
            # print(*pipe_data) 
            MSOP, ii = itools.EffArea_clusters(D,sige,sigu, F, cluster_details, unit = 'MPa')
            print('len MSOP',len(MSOP) )
            # print(ii)
            self.cluster_MSOP = MSOP
            self.df_cluster['MSOP_EffArea'] = MSOP
            self.df_cluster['ERF_EffArea'] = MAOP/MSOP
            
            cluster_id = self.df_Def['Single_idx']==0
            self.df_Def['MSOP_EffArea']=np.nan
            self.df_Def['MSOP_EffArea'][cluster_id] = MSOP
            self.df_Def['ERF_EffArea']=np.nan
            self.df_Def['ERF_EffArea'][cluster_id] = MAOP/MSOP
            
        else:
            print('def_type Not Found: ', def_type, ', expected: Single or Cluster')
        
        # MSOP = itools.comput_MSOP(D,t,dp,L,sige,sigu, unit = 'MPa', method=analysis_type)
        
        
    def xxxCluster_Def_EA(self, cluster_details, analysis_type = sempiric.effective_area):
                
        
        df=self.df_Def
        MAOP = self.MAOP
        sige = self.sige
        sigu = self.sigu
        # Meters
        D  = self.OD/1000
        L  = df.L.values/1000
        t  = df.t.values/1000
        
        dp = df.d.values/100 # dp(%)
        # d  = dp*t
        MSOP = itools.EffArea_clusters(D,t,dp,L,sige,sigu,cluster_details, unit = 'MPa')
        
        
        
    def reliability_analysis(self, semi_empiric = sempiric.modifiedb31g):
        self.MPP=[]
        MAOP = self.MAOP
        sige = self.sige
        sigu = self.sigu
        
        Insp_type   = self.Insp_type
        Confidence  = self.Confid_level
        Accuracy    = self.Accuracy
        # acc_rel     = self.acc_rel
        
        future_analysis = self.future
        
        # meters
        D    = self.OD/1000
        L    = self.df_Def.L.values/1000
        t    = self.df_Def.t.values/1000
        dp   = self.df_Def.d.values/100
        # d    = dp*t
        Ndef = len(dp)
        idx=self.df_Def.index
        PFs = np.zeros(Ndef)
        
        
        Dates=self.date
        for j in range(Ndef):
            
            # if future_analysis:
                # comput std0 and std1, first
                # accuracy[i],conf[i],insp_type[i],tn
            # Reliability_pipe(D,tn,L,d,sige,sigu,Pd=0,insp_type='MFL',accuracy=0.1,conf=0.9,method = semi_empiric.modifiedb31g, asp_ratio=1, future_assessment=False, dates=[]):
            PF_form, beta, MPP, Pd, ii, alpha, StDtd = risk.Reliability_pipe(D, t[j], L[j], dp[j],
                sige, sigu, Pd=MAOP, insp_type=Insp_type,
                 conf=Confidence,  method=semi_empiric , accuracy=Accuracy,
                future_assessment=future_analysis, dates=Dates)
            
            PFs[j] = PF_form
    
            self.df_Def.loc[idx[j],'PF_form']=PF_form
            self.df_Def.loc[idx[j],'beta'] = beta
            self.MPP.append((MPP))
            self.df_Def.loc[idx[j],'Pd'] = Pd
            self.df_Def.loc[idx[j],'FORM Iterations'] = ii
            # self.alpha.append((alpha))
            # self.df_Def.loc[idx[j],'alpha'] = alpha
            self.df_Def.loc[idx[j],'StD d'] = StDtd
    
    ############################################################
    
    def cluster_list(self):
        return self.df_Def.loc[self.df_Def['Single_idx']==0]
    
    def ERF_distrib_create(self):
        ERFs = [0.7, 0.8, 0.9, 0.95, 1]
        ERF_dist=[]
        N0 = 0
        i=0
        for rf in ERFs:
            print(i,rf)
            Nt = sum(self.df_Def.ERF<rf)
            print(i,Nt)
            if i==0:
                ERF_dist.append({'N': Nt-N0 ,
                            'ERF': 'ERF <'+str(ERFs[i]),
                            })          
            else:                    
                ERF_dist.append({'N': Nt-N0 ,
                            'ERF': str(ERFs[i-1])+' - '+str(ERFs[i]),
                            })
            N0 = Nt
            i+=1
        Nt = sum(self.df_Def.ERF>rf)
        ERF_dist.append({'N': Nt ,
                        'ERF': 'ERF >'+str(rf),
                        })
        
        self.ERF_dist = pd.DataFrame(ERF_dist)

    ###################################
    def critical_def_list(self,cluster_details,ERF_lmt = 0.92, plot_cluster=0,print_critical = 1):
    # Printing Critical Defects: ERF>0.99
  
        # if print_critical:
        ERF = self.df_Def['ERF']
        crt_test = (ERF>ERF_lmt)
        id_crit = np.where(crt_test )
        crit_cluster=[]
        crit_defs = []
        ncrtd = sum(crt_test)
        if ncrtd == 0:
            print('No Critical Defects: ERF > ', ERF_lmt)
        else:
            print('Critical Defects: ERF > ',ERF_lmt)
            print('Critical Defects found: ',ncrtd)
        
            j=0
            for i in id_crit[0]:
                j=j+1
                print('Critical Defect: ', j)
                print('Details of Defect : ',i)
                # print(self.dfg.iloc[i])
                
                # Save
                crit_defs.append(
                    self.dfg[[ 
                        'Long. dist [km]', 'Clock Position', 'Depth[%]', 'length [mm]', 'Width [mm]', 't (mm)','ERF', 'Cluster #'
                        ]].iloc[i])
                    
                
                if self.dfg['Cluster #'].iloc[i] >0:
                    # Cluster
                    # print('Cluster details')
                    id_cluster =  self.df_Def['Cluster #'].iloc[i]
                    # print(cluster_details.loc[id_cluster])
                    
                    # Save
                    crit_cluster.append(cluster_details.loc[id_cluster])
                    
                    if plot_cluster:
                        itools.plot_clusters(cluster_details,id_cluster)
            
        
        self.crit_defs=pd.DataFrame(crit_defs)
        self.crit_cluster=crit_cluster
        return crt_test 
    #############################################    
    ##############
    # MAPs
    def plot_map(self, name='', plot_joint=True, plot_defect=True, ERF_min=0.95, ERF_max=1.0, d_min=0.0, save_m=True):

        if len(name)==0:
            name = self.file_name+'_Map'
            
            
        #https://www.movable-type.co.uk/scripts/latlong-utm-mgrs.html
        #Latitude/Northing: n/a / 7585382.088 m
        #Longitude/Easting: n/a / 710594.426 m
        df = self.df_joints.copy()
        ## utm.to_latlon() function may change the Y value, use df = self.df_joints.copy() instead
        
        
        [gn, gl, get_gl]=itools.gridzone_set(df.gridzone.iloc[0], self.grid_letter)
        if get_gl:
            gl = self.grid_letter
        else:
            self.grid_letter = gl
            
        LL=utm.to_latlon(df.X.to_numpy(),df.Y.to_numpy(),int(gn),gl)
        
        LL_mean = np.mean(LL,1)
        m = folium.Map(LL_mean, zoom_starts = 5)
        
        if plot_joint:
            
            coordinates = list(zip(*LL))
            
            folium.PolyLine(
                locations=coordinates,
                color="slategray",
                weight=5,
                tooltip= f"Pipeline xxx  with defects ERF > {ERF_min:.02f} and d > {d_min:.02f}%" ,
            ).add_to(m)
        
        # LL = utm.to_latlon( df.X.to_numpy() , df.X.to_numpy() , df.gridzone.iloc[0], grid_letter)
        # Latitude = LL[0]
        # Longitude = LL[1]
        
        if plot_defect:
        # plot_map('Pipe_joint_Map', joint=true, defect=true)
        ############################################################
        # Plot Defs in map ##############################################
        ############################################################
        
            # self.intact = i.sige*((2*i.t)/i.OD)*i.F
            
            mn_erf =  np.min ([ np.mean (self.df_Def["ERF"] ), ERF_min])
            mx_erf = np.max (self.df_Def["ERF"] )
            ERF_crt = np.min ( [np.round((mx_erf+mn_erf)/2,2), ERF_min])
            
            print('ERF_crt : ',ERF_crt,'ERF_max: ', mx_erf,'ERF_mean: ', mn_erf)
            
            critic = (self.df_Def["ERF"] > ERF_crt) & (self.df_Def["d"] > d_min)
            # df=self.df_Def.copy().loc[critic]
            df_crt = self.df_Def.loc[critic].copy()
            
            print('N critic: ',len(df_crt))
            df_crt.reset_index(drop = True)
            
            
            [gn, gl, get_gl]=itools.gridzone_set(df.gridzone.iloc[0], self.grid_letter)
            if get_gl:
                gl = self.grid_letter
            
            LL=utm.to_latlon(df_crt.X.to_numpy(),df_crt.Y.to_numpy(),int(gn),gl)

            ############################################################
            # ................................... geopandas
            df_crt['Lat'] = LL[0]
            df_crt['Long'] = LL[1]
            gdf = geopd.GeoDataFrame(
                df_crt, geometry=geopd.points_from_xy(df_crt.Long, df_crt.Lat), crs="EPSG:4326"
            )
            
            colormap= cm.LinearColormap(["blue", "green", "yellow", "red", "darkred"], vmin=ERF_crt, vmax=1.0,
                                        caption="ERF")
            
            gdf['ERF']=gdf['ERF'].fillna(0.3)
            gdf['color'] = gdf['ERF'].apply(colormap)
            gdf['radii'] = gdf['d']*3+70 #(gdf['L']**.5)
            # m = folium.Map(location=[(gdf.geometry.y).mean(), (gdf.geometry.x).mean()], zoom_start=4)
            
            name2=name + "Defects GeoData"
            gdf= gdf.drop(['Cluster list'], axis=1)
            folium.GeoJson(gdf, 
                           marker=folium.Circle(radius=10, fill_color="orange", fill_opacity=0.5, color="black", weight=0),
                           tooltip=folium.GeoJsonTooltip(fields=["feature", "ERF", "d", "L", "Lat","Long", 'Cluster #', 'surf_pos']),
                           style_function=lambda x: {
                                    "fillColor": x['properties']['color'],
                                    "radius": x['properties']['radii'],
                                    # "fillOpacity": x['properties']['ERF'],
                                },
                           highlight_function=lambda x: {"fillOpacity": 0.1},# x['properties']['ERF']},
                           zoom_on_click=True,
                           ).add_to(m)
            # folium.GeoJson(gdf, 
            #                marker=folium.Marker(
            #                    icon=folium.DivIcon(html=f"""<div style="font-family: Tahoma ; font-size: 1.5em; color: {color};">{value:.2f}</div>""")
            #                name="Defects GeoData"
            #                ).add_to(m)
            
            # icon=folium.DivIcon(html=f"""<div style="font-family: Verdana; color: collors>{"{:.0f}".format(temp)}</div>""")
            for lat, lon, value, color in zip(gdf['Lat'],gdf['Long'],gdf['ERF'],gdf['color']):
                folium.Marker(location=[lat,lon],
                              icon=folium.DivIcon(html=f"""<div style="font-family: Tahoma ; font-size: 1em; color: {color};"><b>+ &nbsp {value:.2f}<b></div>""")
                              ).add_to(m)
            
            
            colormap.add_to(m)
            
            # https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_marker.html#Use-a-Circle-as-a-Marker
            # folium.GeoJson(
            #     gdf,
                    
                
            if save_m:
                m.save(name2+'.html')
                print("saved Pipi_Defects: "+name)
        
        return m, df_crt
       
##########################################################################
