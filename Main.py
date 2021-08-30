"""
App that takes house price data from the cbs api and uses this to create a dash dashboard.
"""
import pandas as pd
# import requests
# import cbsodata 
# import numpy as np
# import datetime
import dash_table
import dash
import dash_html_components as html
# import plotly.express as px
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.io as pio
pio.renderers.default='browser'
# from plotly.offline import plot
import plotly.graph_objects as go
import Functions as fl

# loads in the cbs data
api='83625NED'
df=fl.loadin_cbsdata(api)
df=fl.cbs_add_date_column(df)
# format columns
df.rename(columns={'GemiddeldeVerkoopprijs_1':'Average_Price'}, inplace=True)
df=df[['RegioS','Perioden','Average_Price']]
id_filt='RegioS'
# gives the inputs for the dropdown based on the id_filt variable
available_indicators = df[id_filt].unique()
# column inputs graph
x="Perioden"
y="Average_Price"
# Static number that determines the pagesize of the table
PAGE_SIZE=10

# dashboard table + graph and dropdown

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# This is needed for the gunicorn heroku setup, turn it off if you want to run it locally.
server=app.server



# This creates the html with the graph and the dropdown
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
])


@app.callback(
    [Output('example-graph', 'figure'),
    Output('example-table','data')],
    # Input('year-slider', 'value'),
    Input('example-table', "page_current"),
    Input('example-table', "page_size"),
    Input('xaxis-column', 'value'))
def update_figure(page_current,page_size,xaxis_column_name):
    """
    

    Parameters
    ----------
    page_current : dash
        Current page of the table.
    page_size : integer
        Static number that determines the pagesize of the table.
    xaxis_column_name : string
        Determines on which city the table is filtered for the column RegioS.

    Returns
    -------
    TYPE
        A figure and table that gives the house prices for a city.

    """
    
    filtered_df=df
    filtered_df=filtered_df[filtered_df[id_filt]==xaxis_column_name]
    df1 = filtered_df.groupby(by=['RegioS', 'Perioden'])['Average_Price'].sum().reset_index()
    average=pd.DataFrame(df[['Perioden','Average_Price']].groupby('Perioden').mean()).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Line(name='Average House Price Netherlands',
        
        x = average['Perioden'],
        y = average['Average_Price']))

    fig.add_trace(go.Bar(name='House Price {}'.format(xaxis_column_name),x=df1[x],y=df1[y]))
        # df1, x=x, y=y,barmode='group', hover_name=y)
    
    fig.update_layout(barmode='group', legend_title="Legend",title="House Prices Netherlands"
    ,xaxis_title="Year",
    yaxis_title="Price",)

    return fig, filtered_df.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)

