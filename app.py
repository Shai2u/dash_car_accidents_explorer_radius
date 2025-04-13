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


def create_pie_chart(df: pd.DataFrame, column_name: str, color_map: dict = None) -> Union[Set, None]:
    """
    Creates a pie chart (donut) figure showing the distribution of values in the specified column.

    Args:
        df (pd.DataFrame): The DataFrame containing the data
        column_name (str): The name of the column to create the pie chart for
        color_map (dict): Dictionary mapping category values to colors. If None, default colors will be used.

    Returns:
        Union[px.Figure, None]: A Plotly Express figure object or None if the column doesn't exist
    """
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
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=75),  # Add top margin for the legend
        annotations=[dict(
            text=f'{len(df)}',
            x=0.5,
            y=0.5,
            font_size=20,
            showarrow=False
        )]
    )
    return fig

def create_grid_scatterplot() -> Set:
    """
    Creates a scatterplot with 100 points arranged in a 5x10 grid.
    
    Returns:
        Set: A Plotly Express figure object with the grid scatterplot
    """
    # Create x and y coordinates for the grid
    x = np.repeat(np.arange(5), 10)  # 5 columns
    y = np.tile(np.arange(10), 5)    # 10 rows
    
    # Create the scatterplot
    fig = px.scatter(x=x, y=y)
    
    # Update layout to make points equal size and remove grid
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(
        template='plotly_white',
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=None
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=None
        ),
        margin=dict(t=0, b=0, l=0, r=0),
        title=None
    )
    
    return fig

app = Dash(__name__)

# Convert GeoDataFrame to GeoJSON
df = pd.read_csv('accidents_2023_processed.csv')
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(
    x=df['lon'], y=df['lat']), crs="EPSG:4326")
gdf = gdf[~gdf.geometry.is_empty].reset_index(drop=True)
gdf_copy = gdf.copy()
center = [32.0853, 34.7818]
columns_list = ['HODESH_TEUNA', 'SUG_DEREH', 'SUG_YOM',
                'YOM_LAYLA', 'YOM_BASHAVUA', 'HUMRAT_TEUNA', 'PNE_KVISH']

# Extract coordinates for KD-tree
points = np.array([(p.x, p.y) for p in gdf_copy.geometry])
tree = cKDTree(points)
# Initialize color dictionary for graphs
col_values_color = {}
for col in columns_list:
    # col_values_color[col]
    items = {}
    for i, item_name in enumerate(df[col].unique()):
        items[str(item_name)] = px.colors.qualitative.Dark24[i]
    col_values_color[col] = items
selected_column = 'HUMRAT_TEUNA'
gdf_copy['color'] = gdf_copy[selected_column].astype(str).map(col_values_color[selected_column])
gdf_json = gdf.copy().__geo_interface__
# Create pie chart
fig = create_pie_chart(df, selected_column, col_values_color[selected_column])
# Hideout dictionary for map

hide_out_dict = {'active_col': selected_column,
                 'circleOptions': {'fillOpacity': 1, 'stroke': False, 'radius': 3.5}
                 }
def assign_point_to_layer():
    """
    Creates a JavaScript function to assign a point to a layer with a specific color.

    The function uses the `active_col` property and the `color_dict` from the context's hideout
    to determine the fill color of the circle marker.

    Returns
    -------
    str
        A string containing the JavaScript function to be used for assigning points to layers.
    """
    point_to_layer = assign("""function(feature, latlng, context){
        const {active_col, circleOptions} = context.hideout;
        circleOptions.fillColor =  feature.properties['color'];
        return L.circleMarker(latlng, circleOptions);  // render a simple circle marker
    }""")
    return point_to_layer



app.layout = html.Div([
    html.H1('Accidents Map'),
    html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='column-selector',
                    options=[{'label': col, 'value': col}
                            for col in columns_list],
                    value='HUMRAT_TEUNA',  # Default value
                    style={'width': '100%', 'marginBottom': '20px'}
                ),
                html.Div([
                    html.Div([
                        html.Label('Circle Radius (KM):'),
                        dcc.Slider(
                            id='radius-slider',
                            min=1000,
                            max=50000,
                            step=1000,
                            value=10000,
                            marks={i: f'{i//1000}' for i in range(1000, 51000, 2000)},
                        )
                    ]),
                    html.Div([
                        html.Label('Selection Mode:'),
                        dcc.RadioItems(
                            id='selection-mode',
                            options=[
                                {'label': 'Radius', 'value': 'radius'},
                                {'label': 'Draw Polygon', 'value': 'polygon'}
                            ],
                            value='radius',
                            labelStyle={'display': 'inline-block', 'margin': '0 10px'}
                        )
                    ])
                ])
            ]),
            html.Div([
                dcc.Graph(id='pie-chart', figure=fig, style={'height': '40vh', 'width': '100%'}),
                dcc.Graph(id='grid-scatterplot', figure=create_grid_scatterplot(), style={'height': '40vh', 'width': '100%'})
            ], style={'width': '100%', 'display': 'flex', 'flexDirection': 'column'})
        ], style={'width': '25%', 'padding': '10px'}),
        html.Div([
            dl.Map([
                dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'),
                dl.GeoJSON(
                    id='accidents-geojson', data=gdf_json,
                    pointToLayer=assign_point_to_layer(),  # how to draw points
                    # onEachFeature=assign_on_each_feature(),  # add (custom) tooltip
                    hideout=hide_out_dict,
                ),
                dl.Circle(center=center, radius=10000, id='circle_polygon',
                          dashArray = '5, 10', fillOpacity = 0, color='black', weight=2),
                dl.Polygon(positions=[center, center, center, center], id='costum_polygon', dashArray = '5, 10', fillOpacity = 0, color='black', weight=2),
                dl.FeatureGroup([dl.EditControl(id="edit_control")])
            ], id = 'accidents-map-object', center=center, zoom=12, style={'width': '100%', 'height': '80vh'}),
            html.Div(id='mouse-position', style={'position': 'absolute', 'bottom': '10px', 'left': '10px', 'zIndex': '1000', 'backgroundColor': 'white', 'padding': '5px', 'borderRadius': '5px'})
        ], style={'width': '75%', 'padding': '10px', 'position': 'relative'})
    ], style={'display': 'flex', 'flexDirection': 'row'})
])


@callback(
    Output('accidents-geojson', 'data'),
    Output('accidents-geojson', 'hideout'),
    Output('pie-chart', 'figure'),
    Output('circle_polygon', 'center'),
    Output('circle_polygon', 'radius'),
    Output("edit_control", "editToolbar"),
    Output("costum_polygon", "positions"),
    Output('radius-slider', 'disabled'),
    Input('column-selector', 'value'),
    Input('accidents-map-object', 'n_clicks'),
    State('accidents-map-object', 'clickData'),
    Input('radius-slider', 'value'),
    Input("edit_control", "geojson"),
    Input('selection-mode', 'value'),
    Input("costum_polygon", "positions")
)
def update_map(selected_column, _, clickdate, radius, edit_geojson, selection_mode, polygon_positions):
    # Create a new GeoDataFrame with color properties
    gdf_copy = gdf.copy()
    gdf_copy['color'] = gdf_copy[selected_column].astype(str).map(col_values_color[selected_column])
    
    # Set center point
    if clickdate:
        center = clickdate['latlng']['lat'], clickdate['latlng']['lng']
        center_point = Point(center[1], center[0])  # Note: Point takes (x,y) = (lon,lat)
        if selection_mode == 'radius':
            polygon_positions = [center, center, center]

            # Create buffer around center point (radius in meters)
            buffer = center_point.buffer((radius/ 111320))
            
            # Find points within buffer using KD-tree
            minx, miny, maxx, maxy = buffer.bounds
            candidates = tree.query_ball_point([(minx + maxx)/2, (miny + maxy)/2], 
                                             r=np.sqrt((maxx-minx)**2 + (maxy-miny)**2)/2)
            
            # Then filter candidates to exact buffer
            filtered_indices = [i for i in candidates if buffer.contains(Point(points[i]))]
            
            # Filter the GeoDataFrame
            gdf_copy = gdf_copy.iloc[filtered_indices]
        else:
            radius = 0
    else:
        center = [32.0853, 34.7818]
    fallback = False
    if selection_mode == 'polygon' and edit_geojson:
        # Convert the GeoJSON to a GeoDataFrame
        edit_gdf = gpd.GeoDataFrame.from_features(edit_geojson)
        if len(edit_gdf) > 0:
            edit_gdf.set_geometry(col='geometry', inplace=True)
            
            # Filter points within the drawn polygon
            points_within = gdf_copy[gdf_copy.geometry.within(edit_gdf.geometry.unary_union)]
            gdf_copy = points_within
            radius = 0
            polygon_positions = [c for c in edit_gdf.iloc[0]['geometry'].exterior.coords]
            polygon_positions = [[item[1], item[0]] for item in polygon_positions]
        else:
            fallback = True

    if (selection_mode == 'polygon') and fallback:
        if polygon_positions:
            # Convert polygon positions to a Polygon object
            coords = [[pos[1], pos[0]] for pos in polygon_positions]  # Convert lat/lng to lon/lat
            if coords:
                polygon = Polygon(coords)
                # Filter points within the polygon
                gdf_copy = gdf_copy[gdf_copy.geometry.within(polygon)]
                radius = 0

    
    hideout = {
        'active_col': selected_column,
        'circleOptions': {'fillOpacity': 1, 'stroke': False, 'radius': 3.5}
    }
    
    return (gdf_copy.__geo_interface__, hideout, 
            create_pie_chart(gdf_copy, selected_column, col_values_color[selected_column]), 
            center, radius, 
            dict(mode="remove", action="clear all"), 
            polygon_positions,
            selection_mode == 'polygon')

if __name__ == '__main__':
    # Create geometry column from lat/lon
    app.run_server(debug=True)
