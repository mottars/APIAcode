# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 22:33:11 2025

@author: MottaRS
"""
import numpy as np

import inspection_tools as itools

# get_spreadsheet_labels, pre_proc_df, find_clusters, comput_MSOP, def_critical_limits

# MAPS
import folium 
import utm
import geopandas as geopd
import branca.colormap as cm

##############
# MAPs

def plot_defect_selection(df, m, grupMark, grupERF, colormap, gn, gl, level = 1, shift_num=0, data_column = 'ERF'):
    
    
    df.reset_index(drop = True)
    
    
    # [gn, gl, get_gl]=itools.gridzone_set(df.gridzone.iloc[0], grid_letter)
    # gl = get_gl
    
    LL=utm.to_latlon(df.X.to_numpy(),df.Y.to_numpy(),int(gn),gl)

    ############################################################
    # ................................... geopandas
    df['Lat'] = LL[0]
    df['Long'] = LL[1]
    gdf = geopd.GeoDataFrame(
        df, geometry=geopd.points_from_xy(df.Long, df.Lat), crs="EPSG:4326"
    )
    
    if level == 1:
        gdf[data_column]=gdf[data_column].fillna(0.3)
        gdf['color'] = gdf[data_column].apply(colormap)
    elif level == 2:
        gdf[data_column]=gdf['ERF_EffArea'].fillna(0.3)
        gdf['color'] = gdf['ERF_EffArea'].apply(colormap)
    elif level == 3:
        gdf[data_column]=gdf['ERF_FEM'].fillna(0.3)
        gdf['color'] = gdf['ERF_FEM'].apply(colormap)
    elif level == 4:
        gdf[data_column]=gdf['PF_form'].fillna(1e-22)
        gdf['color'] = gdf['PF_form'].apply(colormap)

            
    gdf['radii'] = gdf['d']*3+100 #(gdf['L']**.5)
    # m = folium.Map(location=[(gdf.geometry.y).mean(), (gdf.geometry.x).mean()], zoom_start=4)
    
    gdf= gdf.drop(['Cluster list'], axis=1)
    grupMark.add_child(
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
                       )
        )
    # folium.GeoJson(gdf, 
    #                marker=folium.Marker(
    #                    icon=folium.DivIcon(html=f"""<div style="font-family: Tahoma ; font-size: 1.5em; color: {color};">{value:.2f}</div>""")
    #                name="Defects GeoData"
    #                ).add_to(m)
    
    # icon=folium.DivIcon(html=f"""<div style="font-family: Verdana; color: collors>{"{:.0f}".format(temp)}</div>""")
    for lat, lon, value, color in zip(gdf['Lat'],gdf['Long'],gdf[data_column],gdf['color']):
        if shift_num:
            grupERF.add_child(
                folium.Marker(location=[lat,lon],
                              icon=folium.DivIcon(html=f"""<div style="font-family: Tahoma ; font-size: 1em; color: {color};"><b>+<b></div>""")
                              )
                )
            if level == 4:
                grupERF.add_child(
                    folium.Marker(location=[lat+shift_num,lon+shift_num],
                                  icon=folium.DivIcon(html=f"""<div style="font-family: Tahoma ; font-size: 1em; color: {color};"> <b>  {value:.2e} <b> </div>""")
                                  )
                    )
            else:
                grupERF.add_child(
                    folium.Marker(location=[lat+shift_num,lon+shift_num],
                                  icon=folium.DivIcon(html=f"""<div style="font-family: Tahoma ; font-size: 1em; color: {color};"><b> &nbsp {value:.2f}<b></div>""")
                                  )
                    )

        else:
            grupERF.add_child(
                folium.Marker(location=[lat+shift_num,lon+shift_num],
                              icon=folium.DivIcon(html=f"""<div style="font-family: Tahoma ; font-size: 1em; color: {color};"><b>+ &nbsp {value:.2f}<b></div>""")
                              )
                )
    

def plot_map(Inspection, name='', plot_joint=True, plot_defects=True, ERF_min=0.95, ERF_max=1.0, d_min=20.0, PF_crit = 1e-4, save_m=True, max_number_of_features_shown = 5000):

    if len(name)==0:
        name = Inspection.file_name+'_Map'
        
        
    #https://www.movable-type.co.uk/scripts/latlong-utm-mgrs.html
    #Latitude/Northing: n/a / 7585382.088 m
    #Longitude/Easting: n/a / 710594.426 m
    df = Inspection.df_joints.copy()
    ## utm.to_latlon() function may change the Y value, use df = Inspection.df_joints.copy() instead
    
    
    [gn, gl, get_gl]=itools.gridzone_set(df.gridzone.iloc[0], Inspection.grid_letter)
    if get_gl:
        gl = Inspection.grid_letter
    else:
        Inspection.grid_letter = gl
        
    LL=utm.to_latlon(df.X.to_numpy(),df.Y.to_numpy(),int(gn),gl)
    
    LL_mean = np.mean(LL,1)
    m = folium.Map(LL_mean, name = 'Open Map', zoom_starts = 5, control=False)
    folium.TileLayer('opentopomap', show = False, name = 'Topographic Map').add_to(m)
    
    folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        show = False,
       ).add_to(m)
    
    # folium.TileLayer('Stadia.AlidadeSatellite', name = 'Satellite',
    #                  attr =  '&copy; CNES, Distribution Airbus DS, &copy; Airbus DS, &copy; PlanetObserver (Contains Copernicus Data) | &copy; <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>', 
    #                  ).add_to(m)
    
    if plot_joint:
        
        pipe_group = folium.FeatureGroup(name="Pipeline").add_to(m)
        
        coordinates = list(zip(*LL))
        
        pipe_group.add_child(
            folium.PolyLine(
                locations=coordinates,
                color="slategray",
                weight=8,
                tooltip= f"Pipeline xxx {name}" ,
            )
        )
        
    
    
    # LL = utm.to_latlon( df.X.to_numpy() , df.X.to_numpy() , df.gridzone.iloc[0], grid_letter)
    # Latitude = LL[0]
    # Longitude = LL[1]
    
    if plot_defects:
    # plot_map('Pipe_joint_Map', joint=true, defect=true)
    ############################################################
    # Plot Defs in map ##############################################
    ############################################################
        
        # Inspection.intact = i.sige*((2*i.t)/i.OD)*i.F
        
        mn_erf =  np.min ([ np.mean (Inspection.df_Def["ERF"] ), ERF_min])
        mx_erf = np.max (Inspection.df_Def["ERF"] )
        ERF_crt = np.min ( [np.round((mx_erf+mn_erf)/2,2), ERF_min])
        
        print('ERF_crt : ',ERF_crt,'ERF_max: ', mx_erf,'ERF_mean: ', mn_erf)
        
        colormap= cm.LinearColormap(["blue", "green", "yellow", "red", "darkred"], vmin=mn_erf, vmax=1.0,
                                caption="ERF")
        
        ERF_limts = [0.7,0.8,0.85,0.9, 1]
        for i in range(len(ERF_limts)):
            erf0 = ERF_limts[i]
            if i==len(ERF_limts)-1:
                critic = (Inspection.df_Def["ERF"] > erf0) 
                n_selection = sum(critic)
                print('N selection: ', n_selection, ' for ERF> ', erf0 )
                defcts_groups = folium.FeatureGroup(name=f"Defects: {erf0:.02f} < ERF  ({n_selection})", show=False).add_to(m)
                
            else:
                erf1 = ERF_limts[i+1]
                critic = (Inspection.df_Def["ERF"] > erf0) & (Inspection.df_Def["ERF"] < erf1)
                n_selection = sum(critic)
                print('N selection: ', n_selection , ' for ERF> ', erf0, ' < ', erf1 )
                defcts_groups = folium.FeatureGroup(name=f"Defects: {erf0:.02f} < ERF < {erf1:.02f} ({n_selection})", show=False).add_to(m)
            
            if n_selection<max_number_of_features_shown:
                df_crt = Inspection.df_Def.loc[critic].copy()
                # def_ERF_groups = folium.FeatureGroup(name="ERF Critical Defect").add_to(m)
                plot_defect_selection(df_crt, m, defcts_groups, defcts_groups, colormap, gn, gl)
                
        #################################################################
        #################################################################
        # Critical DEFECTS assessment
        critic = (Inspection.df_Def["ERF"] > ERF_crt) & (Inspection.df_Def["d"] > d_min)
        
        n_selection = sum(critic)
        def_mark_group = folium.FeatureGroup(name=f"Critical Defects: ERF > {ERF_crt:.02f}  ({n_selection})").add_to(m)
        print('N critic: ', n_selection)
        # def_ERF_group = folium.FeatureGroup(name="ERF Critical Defect").add_to(m)
        
        df_crt = Inspection.df_Def.loc[critic].copy()        
        plot_defect_selection(df_crt, m, def_mark_group, def_mark_group, colormap, gn, gl)
                
        #################################################################
        #Isolated Defects
        critic = (Inspection.df_Def.Single_idx > 0)
        df_crt = Inspection.df_Def.loc[critic].copy()
        mn_erf =  np.min ([ np.mean (df_crt["ERF"] ), ERF_min])
        mx_erf = np.max (df_crt["ERF"] )
        ERF_crt = np.min ( [np.round((mx_erf+mn_erf)/2,2), 0.9])
        critic = (df_crt["ERF"] > ERF_crt)
        n_selection = sum(critic)
        def_mark_group = folium.FeatureGroup(name=f"Critical Isolated Defects: ERF > {ERF_crt:.02f}  ({n_selection})", show=False).add_to(m)
        print('N critic: ', n_selection)
        df_crt = df_crt.loc[critic].copy()
        plot_defect_selection(df_crt, m, def_mark_group, def_mark_group, colormap, gn, gl)
        
        
        #################################################################
        #Cluster Defects
        critic = (Inspection.df_Def.Single_idx == 0)
        df_crt = Inspection.df_Def.loc[critic].copy()
        mn_erf =  np.min ([ np.mean (df_crt["ERF"] ), ERF_min])
        mx_erf = np.max (df_crt["ERF"] )
        ERF_crt = np.min ( [np.round((mx_erf+mn_erf)/2,2), 0.9])
        critic = (df_crt["ERF"] > ERF_crt)
        n_selection = sum(critic)
        def_mark_group = folium.FeatureGroup(name=f"Critical Cluster Defects: ERF > {ERF_crt:.02f}  ({n_selection})", show=False).add_to(m)
        print('N critic: ', n_selection)
        df_crt = df_crt.loc[critic].copy()
        plot_defect_selection(df_crt, m, def_mark_group, def_mark_group, colormap, gn, gl)
        
        
        #################################################################
        #Cluster Defects:  Level 2 
        def_mark_group = folium.FeatureGroup(name=f"Critical Cluster Defects: Level 2 assessment ERF > {ERF_crt:.02f}  ({n_selection})", show=False).add_to(m)
        plot_defect_selection(df_crt, m, def_mark_group, def_mark_group, colormap, gn, gl, level=2, shift_num  = 0.0002)
        
        
        #################################################################
        #Defects:  Reliability Analysis
        critic = (Inspection.df_Def.PF_form > 0)
        df_crt = Inspection.df_Def.loc[critic]
        mn_PF =  np.min ([ np.mean (df_crt["PF_form"] ), PF_crit])
        mx_PF = np.max (df_crt["PF_form"] )
        PF_crt2 = np.min ( [(mx_PF+mn_PF)/2, PF_crit])
        critic = (df_crt["PF_form"] > PF_crt2)
        n_selection = sum(critic)
        def_mark_group = folium.FeatureGroup(name=f"Critical Defects: Prob. Failure > {PF_crt2}  ({n_selection})", show=False).add_to(m)
        print('N critic: ', n_selection, f'Prob. Failure > {PF_crt2}  ({n_selection})')
        df_crt = df_crt.loc[critic]
        plot_defect_selection(df_crt, m, def_mark_group, def_mark_group, colormap, gn, gl, level=4, shift_num  = -0.0002)
        
        # df=Inspection.df_Def.copy().loc[critic]
        
        # print('N critic: ',len(df_crt))
        
        # plot_defect(df_crt, m, def_mark_group, def_ERF_group, colormap, gn, gl)
        
        
        colormap.add_to(m)
        
        folium.LayerControl(position = 'topleft', collapsed = False, ).add_to(m)
        
        # https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_marker.html#Use-a-Circle-as-a-Marker
        # folium.GeoJson(
        #     gdf,
        
        name2=name + "Defects GeoData"
            
        if save_m:
            m.save(name2+'.html')
            print("saved Pipi_Defects: "+name2)
    
    return m, df_crt
   
##########################################################################