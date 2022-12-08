import base64
import datetime
import io
import plotly.graph_objs as go
import cufflinks as cf

import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from dash import dash_table

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    "graphBackground": "#F8F8F8",
    "background": "#f8f8f8",
    "text": "#505050"
}

app.layout = html.Div(children=[
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={ 
            'width': '60%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'solid',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(dcc.Graph(id='Mygraph')),
    html.H5("Input the amount you want to calculate KKM gain below:"),
    html.Div(dcc.Input(id="input", placeholder="Input the amount", type="number", style={'background-color':'#F8F8F8','margin':'10px','border': '.6px', 'borderStyle':'solid', 'width':'200px', 'height':'40px'})),
    html.H5("Gain from KKM for a three-month period:"),
    html.P(id="output", style={'background-color':'#F8F8F8','margin':'10px','border': '.6px', 'borderStyle':'solid', 'borderRadius': '5px', 'width':'180px', 'height':'25px',  'vertical-align': 'middle', 'padding': '10px'}),
    html.Div(id='output-data-upload')
])

def parse_data(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])
    return df

def calc_gain(amount):
    kkm = 0.14
    kkm_m = 0.14 / 12
    kkm_gain_m = amount * kkm_m #montly interest gain amount
    gain_kkm_3m = amount + 3 * kkm_gain_m
    return str(gain_kkm_3m)

@app.callback(Output('Mygraph', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_graph(contents, filename):
    fig = {
        'layout': go.Layout(
            plot_bgcolor=colors["graphBackground"],
            paper_bgcolor=colors["graphBackground"])
    }

    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df = df.set_index(df.columns[0])
        fig = df.iplot(asFigure=True, kind='scatter', mode='lines+markers', size=1)
    return fig
# gain return for kkm
@app.callback(Output("output", "children"), [Input("input", "value")])
def output_gain_kkm(value):
    return calc_gain(value)


@app.callback(Output('output-data-upload', 'children'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_table(contents, filename):
    table = html.Div()
    
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)

        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=df.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in df.columns]
            ),
            html.Hr(),
            html.Div('Raw Content'),
            html.Pre(contents[0:200] + '...', style={
                'whiteSpace': 'pre-wrap',
                'wordBreak': 'break-all'
            })
        ])
    return table

if __name__ == '__main__':
    app.run_server(debug=True)