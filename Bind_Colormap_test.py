# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 08:47:57 2025

@author: MottaRS

from: https://nbviewer.org/gist/BibMartin/f153aa957ddc5fadc64929abdee9ff2e

folium issue: https://github.com/python-visualization/folium/issues/450
"""

import numpy as np
# import sys
# sys.path.insert(0, 'folium')
# sys.path.insert(0, 'branca')

import branca
import folium
from branca.element import MacroElement

from jinja2 import Template

class BindColormap(MacroElement):
    """Binds a colormap to a given layer.

    Parameters
    ----------
    colormap : branca.colormap.ColorMap
        The colormap to bind.
    """
    def __init__(self, layer, colormap):
        super(BindColormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
            {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }});
            {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }});
        {% endmacro %}
        """)  # noqa
# We create a sample of data thanks to numpy.

lats = 20 * np.cos(np.linspace(0, 2*np.pi, 300))
lons = 20 * np.sin(np.linspace(0, 2*np.pi, 300))
colors = np.sin(5 * np.linspace(0, 2*np.pi, 300))
cm1 = branca.colormap.LinearColormap(['y','orange','r'], vmin=-1, vmax=1, caption='cm1')
cm2 = branca.colormap.LinearColormap(['b','c','g','y','r'], vmin=-1, vmax=1, caption='cm2')
cl1 = folium.features.ColorLine(
    list(zip(lats, lons - 30)),
    colors=colors,
    colormap=cm1,
    weight=10,
    overlay=True,
    name='cl1')
cl2 = folium.features.ColorLine(
    list(zip(lats, lons + 30)),
    colors=colors,
    colormap=cm2,
    weight=10,
    overlay=True,
    name='cl2')

cl3 = folium.features.ColorLine(
    list(zip(lats, lons)),
    colors=colors,
    colormap=cm2,
    weight=10,
    overlay=True,
    name='cl3')
m = folium.Map([0, 0], zoom_start=3)
m.add_child(cm1)
m.add_child(cm2)
group1 = folium.FeatureGroup(name="Critical Isolated Defects", show=False).add_to(m)
group1.add_child(cl1)
group1.add_child(cl2)
group1.add_child(cm1)

group2 = folium.FeatureGroup(name="Grupe 2", show=True).add_to(m)
group2.add_child(cl3)

m.add_child(BindColormap(group1, cm1))
m.add_child(BindColormap(group2, cm2))

folium.LayerControl(position = 'topleft', collapsed = False, ).add_to(m)


m.save('Test_Bind_Colormap'+'.html')