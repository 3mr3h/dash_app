'''
    DeepDive Team, Ekrem Bilgehan Uyar, Sana Basharat, Emre Caglar Hosgor
    12.11.2022
    DI 502
    Prof. Tugba Taskaya Temizel
    Prof. Altan Kocyigit
    
    Python Dash application first version
        depreciated dashboard.
        dashboard for the start of sprint 2.
'''
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

df_usd = pd.read_excel('final_buysell_preds.xls') # for usd calc
end_capital = 0
capital = 0
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
    # KKM GAIN
    html.H5("Capital Amount"),
    html.Div(dcc.Input(id="input_kkm", placeholder=0, type="number", style={'background-color':'#F8F8F8','margin':'10px','border': '.6px', 'borderStyle':'solid', 'width':'200px', 'height':'40px'})),
    
    html.H5("KKM 3 Month Return:"),
    html.P(id="output_kkm", style={'background-color':'#F8F8F8','margin':'10px','border': '.6px', 'borderStyle':'solid', 'borderRadius': '5px', 'width':'180px', 'height':'25px',  'vertical-align': 'middle', 'padding': '10px'}),
    
    # GAIN LOSS calculations expensive
    html.H5("Yearly Inflation:"),
    html.P(dcc.Input(id="interest_rate", placeholder=0, type="number", style={'background-color':'#F8F8F8','margin':'10px','border': '.6px', 'borderStyle':'solid', 'width':'200px', 'height':'40px'})),
    html.H5("Capital gain/loss"),
    html.P(id="output_GL", style={'background-color':'#F8F8F8','margin':'10px','border': '.6px', 'borderStyle':'solid', 'borderRadius': '5px', 'width':'180px', 'height':'25px',  'vertical-align': 'middle', 'padding': '10px'}),
    
    html.H5("Capital Gain/Loss margin"), # %5
    html.Div(id='Output_capital'),
    # Datagrid 
    html.Div(id='output-data-upload')
])

# dataset parsing
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

# figure for the input
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
@app.callback(Output("output_kkm", "children"), [Input("input_kkm", "value")])

def output_gain_kkm(value):
    capital = value
    kkm = 0.14
    if value is None:
        return str(0)
    else:
        gain_kkm_3m = ((kkm/12*3)+1)*value
        end_capital = gain_kkm_3m
        return str(int(gain_kkm_3m))
    
# gain return for usd
@app.callback(Output("output_GL", "children"), [Input("interest_rate", "value")])

def output_gain_loss(value):
    if value is None:
        return str(0)
    else:
        quarterly_inf_rate = value/4
        norm_capital = quarterly_inf_rate/100 * capital + capital
        gain_loss = end_capital - norm_capital
        #return str(gain_loss)
        return end_capital

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
                'wordBreak': 'break-all',
                'width':'%80'
            })
        ])
    return table

# main is over there.
if __name__ == '__main__':
    app.run_server(debug=True)