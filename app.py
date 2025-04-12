from dash import Dash, html
import pandas as pd
import geopandas as gpd
import dash_leaflet as dl
import json

app = Dash(__name__)

# Convert GeoDataFrame to GeoJSON
df = pd.read_csv('accidents_2023_processed.csv')
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(x=df['lon'], y=df['lat']), crs="EPSG:4326")
gdf_json = gdf.copy().__geo_interface__
center = [32.0853, 34.7818]
app.layout = html.Div([
    html.H1('Accidents Map'),
    dl.Map([
        dl.TileLayer(),
        dl.GeoJSON(data=gdf_json, id='accidents-geojson')
    ], center=center, zoom=12, style={'width': '100%', 'height': '50vh'})
])

if __name__ == '__main__':
    
    # Create geometry column from lat/lon
    app.run_server(debug=True)
