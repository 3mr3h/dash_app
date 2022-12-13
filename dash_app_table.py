from dash import Dash, dash_table, html
from dash.dependencies import Input, Output, State

app = Dash(__name__)

app.layout = html.Div([
    dash_table.DataTable(
        id='computed-table',
        columns=[
            {'name': 'Capital', 'id': 'capital'},
            {'name': 'KKM GAIN', 'id': 'kkm'},
            {'name': 'NormCapital', 'id': 'ncapital'},
            {'name': 'Gain/Loss', 'id': 'gainloss'},
            {'name': 'Gain/Loss Margin', 'id': 'GLmargin'}
        ],
        data=[{'capital': (i+1)*10000} for i in range(6)],
        editable=True,
    ),
])

@app.callback(
    Output('computed-table', 'data'),
    Input('computed-table', 'data_timestamp'),
    State('computed-table', 'data'))
def update_columns(timestamp, rows):
    for row in rows:
        kkm = 0.14
        interest = 0.84/4
        try:
            row['kkm'] = float(row['capital']) * (kkm/4+1)
            row['ncapital'] = float(row['capital']) * (interest+1)
            row['gainloss'] = (float(row['capital']) * (kkm/4+1)) - (float(row['capital']) * (interest+1))
            row['GLmargin'] = ((float(row['capital']) * (kkm/4+1)) - (float(row['capital']) * (interest+1))) * 0.05
        except:
            row['kkm'] = 'NA'
            row['ncapital'] = 'NA'
            row['gainloss'] = 'NA'
            row['GLmargin'] = 'NA'
    return rows

if __name__ == '__main__':
    app.run_server(debug=True)
