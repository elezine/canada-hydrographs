# -*- coding: utf-8 -*-

import os
import flask
from random import randint
import re

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import glob as gl

#------------CANADIAN HYDROGRAPH APP MADE WITH DASH AND DEPLOYED ON HEROKU--------------------

# This contains the code needed to run the actual app.

#mapbox_access_token = 'pk.eyJ1IjoiZWxlemluZSIsImEiOiJjazF0djRpdmEwMzFuM3BtdG83bmR6c3p6In0.gc8ylqc0h0kZ48-BJf3D0g'

# SERVER
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0,1000000)))

# APP SETUP
app = dash.Dash(__name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ], server=server,
)

#IMPORTING DATA

rain_coord_dict = pd.read_csv('data/rain_coord_dict.csv')
river_station_ids = rain_coord_dict.river_station.values

river_station_info = pd.read_csv('data/river_stations_info.csv')
river_station_info = river_station_info.set_index(river_station_info['STATION_NUMBER'])
river_station_info = river_station_info.loc[river_station_ids]

river_lats = river_station_info.LATITUDE.values
river_lons = river_station_info.LONGITUDE.values

x = pd.DataFrame(index = river_station_ids, data=[river_lats[i] for i in range(0,len(river_lats))])
y = pd.DataFrame(index = river_station_ids, data=[river_lons[i] for i in range(0,len(river_lons))])
river_geo_data = x.merge(y, how='left', left_index=True, right_index=True)

#actual river data
river_flow = pd.read_csv('data/river_flow.csv')
river_flow.index = river_flow[river_flow.columns[0]].values
river_level = pd.read_csv('data/river_level.csv')
river_level.index = river_level[river_level.columns[0]].values

all_river_dates = pd.to_datetime(river_flow.index,yearfirst=True)
years = np.unique([d.year for d in all_river_dates])
years = years[:].astype(int)

#actual rain data
rain = pd.read_csv('data/rain.csv')
rain.index = rain[rain.columns[0]].values

river_station_names = pd.DataFrame(index = river_station_ids, data = river_station_info['STATION_NAME'])

station_options = [{'label': name, 'value': name} for name in river_station_ids]

dates = ['2005-01-01','2006-01-01','2007-01-01','2008-01-01','2009-01-01','2010-01-01','2011-01-01',
'2012-01-01','2013-01-01','2014-01-01','2015-01-01','2016-01-01','2017-01-01']

# CREATE FIGURES

# RIVER DISCHARGE, LEVEL AND RAIN (TWO AXES - second is level and rain, interchangeable)
#initialize with plot showing discharge and level for one station
graph = make_subplots(specs=[[{"secondary_y": True}]])

trace_flow = go.Scatter(x = river_flow.index, y = river_flow['06HB002'], name='Flow', line= dict(width = 2, color = 'rgb(229,151,50)'))
#trace_level = go.Scatter(x = river_level.index, y = river_level['06HB002'], name='Level', line= dict(width = 2, color = 'rgb(0, 76, 153)'))
trace_rain = go.Scatter(x = rain.index, y = rain['06HB002'], name = 'Rain Fall Rate', line = dict(width = 1, color = 'rgb(0, 76, 153)'))

graph_layout = go.Layout(hovermode = 'closest', xaxis=dict(showgrid=True, zeroline=False, title='Date'),
        yaxis=dict(showgrid=True, zeroline=False, title='Discharge [m^3/s]'), yaxis2 = dict(title='Rain Fall Rate [mm/day]'), height = 400, margin=dict(r=5, l=20, t=0, b=20))

graph.add_trace(trace_flow, secondary_y=False)
graph.add_trace(trace_rain, secondary_y=True)
graph.update_layout(graph_layout)

# MAP OF STATIONS (BOTH RIVER AND RAIN, DIFFERENT COLORS)
geomap = go.Scattergeo(lat = river_lats, lon = river_lons, text = river_station_info['STATION_NAME'].astype(str)) #mapbox(lat = lats, lon = lons, text = station_info['STATION_NAME'].astype(str))
map_layout = go.Layout(hovermode = 'closest',height=400,margin=dict(r=0, l=10, t=0, b=20), geo = dict(
        scope = 'north america',
        showland = True,
        landcolor = "rgb(212, 212, 212)",
        subunitcolor = "rgb(255, 255, 255)",
        countrycolor = "rgb(255, 255, 255)",
        showlakes = True,
        lakecolor = "rgb(255, 255, 255)",
        showsubunits = True,
        showcountries = True,
        resolution = 50,
        projection = dict(
            type = 'conic conformal',
            rotation_lon = -100
        ),
        lonaxis = dict(
            showgrid = True,
            gridwidth = 0.5,
            range= [ -138.0, -87.0 ],
            dtick = 5
        ),
        lataxis = dict (
            showgrid = True,
            gridwidth = 0.5,
            range= [ 45.0, 75.0 ],
            dtick = 5
        )
    ))

#mapbox code below uses satellite imagery but I couldn't get it to zoom in
'''
mapbox = go.layout.Mapbox(
        accesstoken = mapbox_access_token,
        bearing = 0,
        center = go.layout.mapbox.Center(lat=60.0, lon=-110),
        pitch = 0,
        zoom = 2,
        #mapbox_style = "white-bg",
        layers = [{
    'below':'traces',
    'sourcetype':'raster',
    'source': ["https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"]
}]
)
)
'''

map = go.Figure(data = [geomap], layout = map_layout)


# DASH LAYOUT FOR APP

app.layout = html.Div([

    # TITLE
    html.Div([
        html.H1('Canada Water Flow Data'),
        html.P('Discharge data taken from:'),
        html.P([html.A('National Water Data Archive HYDAT database',href='https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/monitoring/survey/data-products-services/national-archive-hydat.html')]),
        html.P('Rain fall data taken from:'),
        html.P([html.A('ERA5 Reanalysis Data Product', href='https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview')])
        ],
        style = {'padding': '50px'}),

    # STATION NAME
    html.Div([
        html.P(id = 'station_title', children = 'Station')
    ]),

    # TWO PANEL GRAPH (LEFT) AND MAP (RIGHT)
    html.Div(
        className = 'row',
        children=[

            # DISCHARGE/LEVEL/RAIN GRAPH
            html.Div(
                className = "six columns",
                children=html.Div([

                    # GRAPH
                    html.Div(
                        children = dcc.Graph(
                                    id='discharge graph',
                                    figure = graph),
                        ),

                    # TIME SLIDER (BELOW)
                    html.P([
                        html.Label('choose a year'),
                        dcc.RangeSlider(id = 'year slider',
                                        marks = {i : dates[i][0:4] for i in range(0, len(dates))},
                                        min = 0,
                                        max = len(years)-1,
                                        value = [1,2]),
                            ]),

                ]),
                ),

                # MAP OF GAUGE LOCATIONS
                html.Div(
                    className = 'six columns',
                    children = html.Div([

                        # MAP
                        html.Div(
                            children = dcc.Graph(
                                        id = 'map',
                                        figure = map),
                            ),

                        # STATION CHOICES DROP-DOWN
                        html.Div([
                            html.P([
                                html.Label("choose a station"),
                                dcc.Dropdown(id = 'station options',
                                options = station_options,
                                value = '06HB002')
                                ]),
                        ]),
                    ]),
                ),
            ]),
        ])


# CALLBACKS (ACTIVELY CHANGE APP)

# CHANGE STATION TITLE DEPENDING ON WHICH STATION
@app.callback(Output('station_title','children'),
            [Input('station options','value')])

def update_title(input1):
    return river_station_names.loc[input1][0]

# CHANGE DISCHARGE PLOT DEPENDING ON WHICH STATION and YEAR
@app.callback(Output('discharge graph', 'figure'),
            [Input('station options', 'value'),
            Input('year slider','value')])

def update_figure(input1,input2):
    #filtering the data

    df_flow = river_flow[(river_flow.index > dates[input2[0]]) & (river_flow.index < dates[input2[1]])]
    df_rain = rain[(rain.index > dates[input2[0]]) & (rain.index < dates[input2[1]])]

    names = ['Level', 'Rain Fall']

    trace2_flow = go.Scatter(x = df_flow.index, y = df_flow[input1],
                        name = 'Flow',
                        line = dict(width = 2,
                                    color = 'rgb(106, 181, 135)'))

    trace2_rain = go.Scatter(x = df_rain.index, y = df_rain[input1],
                        name = 'Rain',
                        line = dict(width = 1,
                                    color = 'rgb(0, 76, 153)'))

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(trace2_flow, secondary_y=False)
    fig.add_trace(trace2_rain, secondary_y=True)

    fig.update_layout(graph_layout)

    return fig

# CHANGE MAP DEPENDING ON WHICH STATION
@app.callback(Output('map','figure'),
            [Input('station options', 'value')])

def update_map(input1):

    geomap = go.Scattergeo(lat = np.asarray(river_geo_data.loc[input1][0]), lon = np.asarray(river_geo_data.loc[input1][1]), text = river_station_info.loc[input1].STATION_NAME) #mapbox(lat = np.asarray(geo_data.loc[input1][0]), lon = np.asarray(geo_data.loc[input1][1]), text = station_info.loc[input1].STATION_NAME)

    fig = go.Figure(data = [geomap], layout = map_layout)
    return fig


# INITIALIZE APP TO SERVER
if __name__ == '__main__':
    app.server.run(debug = True, threaded=True)
