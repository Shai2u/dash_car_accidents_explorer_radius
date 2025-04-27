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

def generate_donut_chart(df: pd.DataFrame, column_name: str, color_map: dict = None) -> Union[Set, None]:
    if column_name not in df.columns:
        return None

    # If color_map is provided, create a color sequence based on the data order
    if color_map:
        unique_values = df[column_name].unique()
        fig = px.pie(df, names=column_name,
                     hole=0.4,
                     color=column_name, 
                     color_discrete_map=color_map)
    else:
        fig = px.pie(df, names=column_name,
                     hole=0.4)

    fig.update_traces(textposition='inside', textinfo='percent')
    fig.update_layout(
        xaxis_title=label_value[column_name],
        yaxis_title='Percentage (%)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=75, b=0, l=0, r=0),  # Minimize margins
        annotations=[dict(
            text=f'{len(df)}',
            x=0.5,
            y=0.5,
            font_size=20,
            showarrow=False
        )],
        autosize=True  # Allow the chart to automatically size itself
    )
    return fig

def generate_scatterplot(df: pd.DataFrame, column_name: str, color_map: dict = None) -> Union[Set, None]:
    if column_name not in df.columns:
        return None
    
    # Calculate normalized counts (as percentages)
    value_counts = df[column_name].value_counts()
    normalized_counts = (value_counts / len(df)) * 100
    
    # Create a DataFrame for plotting
    plot_df = pd.DataFrame({
        column_name : normalized_counts.index,
        'Normalized_Count': normalized_counts.values
    })
    
    if color_map:
        fig = px.scatter(plot_df, 
                        x=column_name, 
                        y='Normalized_Count',
                        color=column_name,
                        color_discrete_map=color_map)
    else:
        fig = px.scatter(plot_df, 
                        x=column_name, 
                        y='Normalized_Count')
    
    fig.update_traces(marker=dict(size=12))
    fig.update_layout(
        title=f'Distribution of {label_value[column_name]} (%)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title='Percentage (%)',
        xaxis_title=label_value[column_name]
    )
    return fig 




### Load Data
df = pd.read_csv('accidents_2023_processed.csv')

# Set parameters
center = (32.0853, 34.7915)

columns_list = ['HODESH_TEUNA', 'SUG_DEREH', 'SUG_YOM',
                'YOM_LAYLA', 'YOM_BASHAVUA', 'HUMRAT_TEUNA', 'PNE_KVISH']
label_value = {'HODESH_TEUNA': 'Month', 'SUG_DEREH': 'Road Type', 'SUG_YOM': 'Day Type',
                'YOM_LAYLA': 'Day Night', 'YOM_BASHAVUA': 'Day of a week', 'HUMRAT_TEUNA': 'Severity', 'PNE_KVISH': 'Road Surface'}
# Define dropdown options
dropdown_options = [ {'label': label_value[key], 'value': key} for key in label_value]


col_values_color = {}
for col in columns_list:
    # col_values_color[col]
    items = {}
    for i, item_name in enumerate(df[col].unique()):
        items[str(item_name)] = px.colors.qualitative.Dark24[i]
    col_values_color[col] = items


#### Prepare pie-chart
selected_column = 'HUMRAT_TEUNA'
fig_pie_chart = generate_donut_chart(df, selected_column, col_values_color[selected_column])

# fig_pie_chart = generate_donut_chart()
bar_chart = generate_scatterplot(df, selected_column, col_values_color[selected_column])

app = Dash(__name__)
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
                dcc.Graph(id='pie-chart', figure=fig_pie_chart),
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

