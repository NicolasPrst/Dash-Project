# -*- coding: utf-8 -*-
"""
Code utilisant le framework Dash pour afficher les données
Set up de geofencing

Groupe Iot Asset Tracking
"""

#-------------------Imports--------------------

import pandas as pd
import numpy as np
import dash                     
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
    
import plotly.graph_objects as go

import random

#-------------------Mapbox Token---------------
#Set the mapbox token needed to load the map. 
#The token is specific for a particular map.

mapbox_access_token = 'pk.eyJ1Ijoid2FlbnQiLCJhIjoiY2t3dXB6czQyMWJyODJwbHM2eDVndjMyNSJ9.70m0Vzif_iEuCqbEdCc0Hw'

#-------------------Read CSV--------------------
#Load the CSV and get the data in a dataframe

data = pd.read_csv("C:/Users/Nicolas Prst/Documents/data.csv", sep=';')
df = pd.DataFrame(data, 
                  columns=['mac_adress', 'timestamp', 'Altitude', 'CPU_Temperature', 'Latitude', 'Longitude', 'Colors']
                  )

#--------------Set Colors----------------
#Set a color for each different mac address
#The colors will be shawn on dash server

for element in df['mac_adress'].unique():
    color_list = pd.Series(["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])])
    df['Colors'] = np.where(df['mac_adress'] == element, 
                            color_list, 
                            df['Colors'])
    

#--------------Convert timestamp----------------

df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

#-------------------Set up Dash server----------

app = dash.Dash(__name__)

blackbold={'color':'black', 'font-weight': 'bold'} #Writing style

app.layout = html.Div([
    html.Div([
        html.Div([
            
            #MAC address checklist       
            html.Label(children=['Mac Adress: '], style=blackbold),
            dcc.Checklist(id='MAC_address_checklist',
                options=[{'label':str(b),'value':b} for b in sorted(df['mac_adress'].unique())],
                value=[b for b in sorted(df['mac_adress'].unique())],
            ),
            
        ], className='data_filters'
        ),
        
        html.Div([
            
            # Map
            dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
                style={'background':'#00FC87','padding-bottom':'2px','padding-left':'2px','height':'100vh'}
            ),
            
        ], className='Map_printing'
        ),
        
    ]),
        
])

#-----------------------------------------------

@app.callback(Output('graph', 'figure'),
              [Input('MAC_address_checklist', 'value')])

def update_output(mac_add):
    
    df_sub = df[(df['mac_adress'].isin(mac_add))]  
    
    customdata_datetime = [pd.to_datetime(each_date).strftime("%d/%m/%Y  %H:%M") for each_date in df_sub['timestamp']]
    
    customdata = np.stack((df_sub['Altitude'], 
                           df_sub['CPU_Temperature'], 
                           df_sub['mac_adress'],
                           customdata_datetime),
                          axis=-1)
    
    fig = [go.Scattermapbox(
        lat= df_sub['Latitude'],
        lon= df_sub['Longitude'],
        mode='markers',
        marker={'color' : df_sub['Colors']},
        unselected={'marker' : {'opacity':1}},
        selected={'marker' : {'opacity':0.5, 'size':25}},
        hoverinfo='text',
        customdata= customdata,
        hovertemplate="Mac adress: %{customdata[2]}<br>"+
                      "Timestamp: %{customdata[3]}<br>"+
                      "Lat: %{lat}<br>"+
                      "Lon: %{lon}<br>"+
                      "Altitude: %{customdata[0]}<br>"+
                      "CPU Temp: %{customdata[1]}<br>"
        )]
    
    return {
        'data': fig,
        'layout': go.Layout(
            hovermode='closest',
            hoverdistance=2,
            title=dict(text="Mapping of devices",font=dict(size=50, color='red')),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=25,
                style='basic',
                center=dict(
                    lat=48.814,
                    lon=2.377
                ),
                pitch=40,
                zoom=15
            ),
        )
    }
    


#-------------------Main------------------------

if __name__ == '__main__':
    app.run_server(debug=True)