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
import plotly.express as px
import pandas as pd

def generate_donut_chart():
    # Sample data - replace with your actual data
    data = {
        'Category': ['A', 'B', 'C', 'D'],
        'Value': [30, 25, 20, 25]
    }
    df = pd.DataFrame(data)
    
    fig = px.pie(df, values='Value', names='Category', hole=0.4)
    fig.update_layout(
        title='Accident Distribution',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def generate_scatterplot():
    # Sample data - replace with your actual data
    data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'Accidents': [100, 120, 90, 150, 110]
    }
    df = pd.DataFrame(data)
    
    fig = px.scatter(df, x='Month', y='Accidents')
    fig.update_traces(marker=dict(size=12)) 
    fig.update_layout(
        title='Monthly Accident Statistics',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig 

pie_chart = generate_donut_chart()
bar_chart = generate_scatterplot()

# Define dropdown options
dropdown_options = [
    {'label': 'Option 1', 'value': 'opt1'},
    {'label': 'Option 2', 'value': 'opt2'},
    {'label': 'Option 3', 'value': 'opt3'}
]

app = Dash(__name__)
center = (32.0853, 34.7915)
app.layout = html.Div([
    html.Div( 
    [html.H1('Query Statisitcs with Geometry - Car Accidents')],
     style={'textAlign': 'center', 'height': '5vh'}
    ),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Label('Select Category:'),
                    dcc.Dropdown(
                        id='category-dropdown',
                        options=dropdown_options,
                        value='opt1',
                        style={'width': '100%', 'marginBottom': '20px', 'fontSize': '20px'}
                    )
                ]),
                html.Div([
                    html.Label('Distance (km):'),
                    dcc.Slider(
                        id='distance-slider',
                        min=0,
                        max=50,
                        step=5,
                        value=10,
                        marks={i: {'label': str(i), 'style': {'fontSize': '20px'}} for i in range(0, 51, 2)},
                        tooltip={"placement": "bottom", "always_visible": True, "style": {"fontSize": "20px"}}
                    )
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Label('Selection Mode:'),
                    dcc.RadioItems(
                        id='selection-radio',
                        options=[
                            {'label': 'Draw', 'value': 'draw'},
                            {'label': 'Buffer', 'value': 'buffer'}
                        ],
                        value='draw',
                        labelStyle={'display': 'inline-block', 'margin': '10px 20px', 'fontSize': '20px'}
                    )
                ])
            ]),
            html.Div([
                dcc.Graph(id='pie-chart', figure=pie_chart),
                dcc.Graph(id='bar-chart', figure=bar_chart)
            ], style={'width': '100%', 'display': 'flex', 'flexDirection': 'column'})
        ], style={'width': '20%', 'padding': '2px'}),
        html.Div([dl.Map([
                dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'),]
                , id = 'accidents-map-object', center=center, zoom=12, style={'width': '100%', 'height': '90vh'})
            
        ], style={'width': '80%', 'padding': '5px', 'position': 'relative', 'textAlign': 'center', 'height': '90vh'})
    ], style={'display': 'flex', 'flexDirection': 'row'})
])


if __name__ == '__main__':
    # Create geometry column from lat/lon
    app.run_server(debug=False)

