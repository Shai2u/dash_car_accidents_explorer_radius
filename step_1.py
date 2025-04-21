"""
Author: Shai Sussman
Date: 2025-04-12
Description: This application provides an interactive visualization of Israeli election data using Dash.

Key Features:
- 
"""
from dash import Dash, html, dcc, Input, Output, callback, State
from dash_extensions.javascript import assign
import pandas as pd
import geopandas as gpd
import dash_leaflet as dl
import plotly.express as px
import json
from typing import Union, Set
from shapely.geometry import Point, Polygon
from scipy.spatial import cKDTree
import numpy as np


app = Dash(__name__)

app.layout = html.Div([
    html.Div( 
    [html.H1('Query Statisitcs with Geometry - Car Accidents')],
     style={'textAlign': 'center',  'backgroundColor': '#ADD8E6', 'height': '5vh'}
    ),
    html.Div([
        html.Div([
            html.Div([
                html.H3('DROP MENU COLUMNS',style={'height': '3vh'}),
                html.Div([html.H3('DISTANCE SELECTION', style={'height': '3vh'}),
                          html.H3('RADIO SELECTION DRAW OR BUFFER', style={'height': '3vh'})
                ])
            ]),
            html.Div([
                html.H3('PIE CHART' , style={'height': '30vh'}),
                html.H3('DOT MATRIX GRAPH', style={'height': '30vh'})
            ], style={'width': '100%', 'display': 'flex', 'flexDirection': 'column'})
        ], style={'width': '20%', 'padding': '2px', 'backgroundColor': '#DAA520'}),
        html.Div([html.H3("MAP LOCATION")
        ], style={'width': '80%', 'padding': '5px', 'position': 'relative', 'backgroundColor': '#90EE90', 'textAlign': 'center', 'height': '90vh'})
    ], style={'display': 'flex', 'flexDirection': 'row'})
])


if __name__ == '__main__':
    # Create geometry column from lat/lon
    app.run_server(debug=False)

