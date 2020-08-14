import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import MySQLdb as dbapi
import time, os
import MySQLdb.cursors as cursors
import json
import os, time
from dash.dependencies import Output, Input
import plotly.io as pio
import plotly.graph_objects as go
import numpy as np
import random



external_stylesheets = ['https://codepen.io/lt47/pen/MWyamZe.css']
#external_scripts = []
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def random_timestamps(start, end, n=7):

    start_u = start.value//10**9
    end_u = end.value//10**9

    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='s')


start = pd.to_datetime('2020-07-01')
end = pd.to_datetime('2020-08-24')

leggo = random_timestamps(start, end)


EMPLOYEE_ID = ['023453', '687942', '472632',
               '231431', '462389', '398348', '276418']

CRANE_ID = ['Crane 1', 'Crane 2', 'Crane 3',
            'Crane 4', 'Crane 5', 'Crane 6', 'Crane 7']

ENTRY_DATE = leggo

DUE_DATE = leggo + pd.to_timedelta(8, unit='h')

EXP_LABELS = ['Inspection Due', 'Up-to-date']

INSP_LABELS = ['OK', 'Failed', 'Marginal']

EXP_STATUS = random.choices(EXP_LABELS, k=7)

INSP_STATUS = random.choices(INSP_LABELS, k=7)

CONTRIVED_DATA = list(zip(EMPLOYEE_ID, CRANE_ID, ENTRY_DATE,
                          DUE_DATE, EXP_STATUS, INSP_STATUS))

df = pd.DataFrame(CONTRIVED_DATA, columns=[
                  'Employee ID', 'Crane ID', 'Inspection Date', 'Must Inspect By', 'Expiration Status', 'Crane Status'])


def lets_go():
    dfg = df.groupby('Crane Status').count().reset_index()
    dfh = df.groupby('Expiration Status').count().reset_index()
    fig = px.bar(dfg, x="Crane Status", y="Crane ID",
                 color="Crane Status", barmode="stack", width=500,
                 height=500, color_discrete_map={
                     "Failed": "red",
                     "OK": "green",
                     "Marginal": "goldenrod"})
    fig2 = px.bar(dfh, x="Expiration Status", y="Crane ID",
                  color="Expiration Status", barmode="stack", width=500,
                  height=500, color_discrete_map={
                      "Inspection Due": "red",
                      "Up-to-date": "green"}, title="8 Hour Insp. Cycle")
    layout = {'autosize': False, 'height': 670, 'width': 690,
              'plot_bgcolor': 'rgb(255,255,255)', 'paper_bgcolor': 'rgb(128, 128, 128)',
              'bargap': 0.3, 'xaxis_tickfont_size': 16, 'yaxis_tickfont_size': 15,
              'font_family': 'calibri', 'font_size': 16, 'font_color': 'white'}
    fig['layout'].update(layout)
    fig2['layout'].update(layout)
    return html.Div(children=[
        html.H2(children='Operators\' Inspection Report', style={
                'font-family': 'calibri', 'font-weight': 'bold', 'color': 'black',
                'align-items': 'center', 'text-align': 'center',
                'font-size': '37px', 'padding-top': '80px'}),
        html.Div(className='tickerlabel',
                 children=html.P('expired inspections')),
        html.Div(id='ticker', className='ticker',
                 children=html.P(id='tickertext')),
        html.Div(className='tickerlabel',
                 children=html.P('failed inspections!')),
        html.Div(id='ticker1', className='ticker1',
                 children=html.P(id='tickertext1')),
        html.Div(className='graph-parent', children=[
            html.Div(dcc.Graph(
                id='graph',
                figure=fig,
                config={'displaylogo': False}), className='graph-one'),
            html.Div(dcc.Graph(
                id='graph2',
                figure=fig2,
                config={'displaylogo': False}
            ), className='graph-two')
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'margin': 'auto'}),

        dash_table.DataTable(
            id='table',
            data=df.to_dict('records'),
            sort_action='native',
            columns=[{"name": i, "id": i} for i in df.columns],
            editable=True,
            style_header={'backgroundColor': 'rgb(30, 30, 30)',
                          'fontWeight': 'bold',
                          'fontSize': '23px',
                          'fontFamily': 'calibri',
                          'textAlign': 'center'
                          },
            style_cell={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white',
                'height': 'auto',
                'whiteSpace': 'normal',
                'textAlign': 'center'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_data_conditional=[
                {
                    'if': {
                        'column_id': 'Employee ID',
                    },
                    'backgroundColor': 'gray',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{Crane Status} = "OK"',
                        'column_id': 'Crane Status'
                    },
                    'backgroundColor': 'green',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{Crane Status} = "Marginal"',
                        'column_id': 'Crane Status'
                    },
                    'backgroundColor': 'yellow',
                    'color': 'black'
                },
                {
                    'if': {
                        'filter_query': '{Crane Status} = "Failed"',
                        'column_id': 'Crane Status'
                    },
                    'backgroundColor': 'red',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{Expiration Status} = "Inspection Due"',
                        'column_id': 'Expiration Status'
                    },
                    'backgroundColor': 'red',
                    'color': 'white'
                },
                {
                    'if': {
                        'filter_query': '{Expiration Status} = "Up-to-date"',
                        'column_id': 'Expiration Status'
                    },
                    'backgroundColor': 'green',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_editable': False  # True | False
                    },
                    'backgroundColor': 'rgb(240, 240, 240)',
                    # 'cursor': 'not-allowed'
                    'cursor': 'allowed'
                },
                {
                    'if': {
                        'column_type': 'any'  # 'text' | 'any' | 'datetime' | 'numeric'
                    },
                    'textAlign': 'center',
                    'fontSize': '22px',
                    'fontFamily': 'calibri'
                },
                {
                    'if': {
                        'state': 'active'  # 'active' | 'selected'
                    },
                    'backgroundColor': 'rgba(0, 116, 217, 0.3)'
                }
            ]
        )
    ], style={'background-color': 'white'})


@app.callback(
    [dash.dependencies.Output('tickertext', 'children'),
     dash.dependencies.Output('tickertext1', 'children')
     ],
    [dash.dependencies.Input('table', 'data')])
def update_figure(dropselection):
    newdf = df[df['Expiration Status'].str.contains("Inspection Due")]
    inspdf = df[df['Crane Status'].str.contains("Failed|Marginal")]

    nudf = newdf['Crane ID']
    nuinspdf = inspdf['Crane ID']

    nunudf = ", ".join(nudf)
    nunuinspdf = ", ".join(nuinspdf)
    return (nunudf, nunuinspdf)


app.layout = lets_go


if __name__ == '__main__':
    app.run_server(debug=True)
