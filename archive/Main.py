# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 10:20:36 2021

@author: flori
"""
import pandas as pd
import requests
import cbsodata 
import numpy as np
import datetime

import dash_table
import dash
import dash_html_components as html
import plotly.express as px
import dash_core_components as dcc
from dash.dependencies import Input, Output
# import plotly.io as pio
# pio.renderers.default='browser'



import Functions as fl
api='83625NED'
df=fl.loadin_cbsdata(api)
df=fl.cbs_add_date_column(df)
df.rename(columns={'GemiddeldeVerkoopprijs_1':'Average_Price'}, inplace=True)
id_filt='RegioS'
available_indicators = df[id_filt].unique()
x="Perioden"
y="Average_Price"


# dashboard table + graph and dropdown
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server

PAGE_SIZE=30

app.layout = html.Div(children=[
    html.H4(children='CBS'),
    # generate_table(df),
    dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Amsterdam'
            ),
        dcc.Graph(
        id='example-graph'
        # ,
        # figure=fig
    )
    ,
    dash_table.DataTable(
    id='example-table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    page_current=0,
    page_size=PAGE_SIZE,
    page_action='custom' 
    )
    #     dcc.Slider(
    #     id='year-slider',
    #     min=df[y].min(),
    #     max=df[y].max(),
    #     value=df[y].min(),
    #     marks={str(state): str(state) for state in df[y].unique()},
    #     step=None
    # ),
                    
    
    
    # dcc.Graph(id='life-exp-vs-gdp',figure=graph_total())
    # ,
    #     dcc.Dropdown(
    #             id='input_cat',
    #             options=[{'label': i, 'value': i} for i in year],
    #             value='2016'
    #         )
    # , html.Div(id='example-table')

    
            
        # ,
    
])
# https://dash.plotly.com/datatable/callbacks

@app.callback(
    [Output('example-graph', 'figure'),
    Output('example-table','data')],
    # Input('year-slider', 'value'),
    Input('example-table', "page_current"),
    Input('example-table', "page_size"),
    Input('xaxis-column', 'value'))
def update_figure(page_current,page_size,xaxis_column_name):
    # filtered_df = df[df[y] == selected_year]
    filtered_df=df
    filtered_df=filtered_df[filtered_df[id_filt]==xaxis_column_name]
    df1 = filtered_df.groupby(by=['RegioS', 'Perioden'])['Average_Price'].sum().reset_index()
    
    fig = px.bar(df1, x=x, y=y,barmode='group', hover_name=y)

    fig.update_layout(transition_duration=500)

    return fig, filtered_df.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
