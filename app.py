"""
Author: Shai Sussman
Date: 2025-04-12
Description: This application provides an interactive visualization of Israeli election data using Dash.

Key Features:
- 
"""
from dash import Dash, html, dcc
import pandas as pd
import geopandas as gpd
import dash_leaflet as dl
import plotly.express as px
import json
from typing import Union

def create_pie_chart(df: pd.DataFrame, column_name: str) -> Union[set, None]:
    """
    Creates a pie chart (donut) figure showing the distribution of values in the specified column.
    
    Args:
        df (pd.DataFrame): The DataFrame containing the data
        column_name (str): The name of the column to create the pie chart for
        
    Returns:
        Union[px.Figure, None]: A Plotly Express figure object or None if the column doesn't exist
    """
    if column_name not in df.columns:
        return None
        
    fig = px.pie(df, names=column_name, 
                 title=f'Distribution of {column_name}',
                 hole=0.4)  # Creates a donut chart
    fig.update_traces(textposition='inside', textinfo='percent')
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=100),  # Add top margin for the legend
        annotations=[dict(
            text=f'{len(df)}',
            x=0.5,
            y=0.5,
            font_size=20,
            showarrow=False
        )]
    )
    return fig

app = Dash(__name__)

# Convert GeoDataFrame to GeoJSON
df = pd.read_csv('accidents_2023_processed.csv')
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(x=df['lon'], y=df['lat']), crs="EPSG:4326")
gdf_json = gdf.copy().__geo_interface__
center = [32.0853, 34.7818]
columns_list =['HODESH_TEUNA', 'SUG_DEREH', 'SUG_YOM',
       'YOM_LAYLA', 'YOM_BASHAVUA', 'HUMRAT_TEUNA', 'PNE_KVISH']

# Create pie chart
fig = create_pie_chart(df, 'HUMRAT_TEUNA')

app.layout = html.Div([
    html.H1('Accidents Map'),
    html.Div([
        html.Div([
            html.Div(dcc.Graph(figure=fig), style={'width': '100%', 'height': '80vh'})
        ], style={'width': '25%', 'padding': '10px'}),
        html.Div([
            dl.Map([
                dl.TileLayer(),
                dl.GeoJSON(data=gdf_json, id='accidents-geojson')
            ], center=center, zoom=12, style={'width': '100%', 'height': '80vh'})
            ], style={'width': '75%', 'padding': '10px'})
    ], style={'display': 'flex', 'flexDirection': 'row'})
])

if __name__ == '__main__':
    # Create geometry column from lat/lon
    app.run_server(debug=True)
