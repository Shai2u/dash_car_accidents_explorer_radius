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
                     title=f'Distribution of {column_name}',
                     hole=0.4,
                     color=column_name, 
                     color_discrete_map=color_map)
    else:
        fig = px.pie(df, names=column_name,
                     title=f'Distribution of {column_name}',
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
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(
    x=df['lon'], y=df['lat']), crs="EPSG:4326")
gdf_copy = gdf.copy()
center = [32.0853, 34.7818]
columns_list = ['HODESH_TEUNA', 'SUG_DEREH', 'SUG_YOM',
                'YOM_LAYLA', 'YOM_BASHAVUA', 'HUMRAT_TEUNA', 'PNE_KVISH']


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
                    html.Label('Circle Radius (KM):'),
                    dcc.Slider(
                        id='radius-slider',
                        min=1000,
                        max=50000,
                        step=1000,
                        value=10000,
                        marks={i: f'{i//1000}' for i in range(1000, 51000, 2000)},
                    )
                ], style={'marginTop': '20px'})
            ]),
            html.Div(dcc.Graph(id='pie-chart', figure=fig),
                    style={'width': '100%', 'height': '80vh'})
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
                dl.Circle(center=center, radius=10000, id='circle_polygon')
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
    Input('column-selector', 'value'),
    Input('accidents-map-object', 'n_clicks'),
    State('accidents-map-object', 'clickData'),
    Input('radius-slider', 'value')
)
def update_map_colors(selected_column, _, clickdate, radius):
    # Create a new GeoJSON with color properties
    if clickdate:
        center = clickdate['latlng']['lat'], clickdate['latlng']['lng']
    else:
        center = [32.0853, 34.7818]

    gdf_copy = gdf.copy()
    gdf_copy['color'] = gdf_copy[selected_column].astype(str).map(col_values_color[selected_column])
    hideout={
            'active_col': selected_column,
            'circleOptions': {'fillOpacity': 1, 'stroke': False, 'radius': 3.5}
            }
    return gdf_copy.__geo_interface__, hideout, create_pie_chart(df, selected_column, col_values_color[selected_column]), center, radius


if __name__ == '__main__':
    # Create geometry column from lat/lon
    app.run_server(debug=True)
