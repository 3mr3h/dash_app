'''
    DeepDive Team, Ekrem Bilgehan Uyar, Sana Basharat, Emre Caglar Hosgor
    03.12.2022
    DI 502
    Prof. Tugba Taskaya Temizel
    Prof. Altan Kocyigit
    
    Python Dash-based implementation for displaying
        the investment recommendations to a user via dynamically updated table.
'''
# Dash imports
from dash import Dash, dash_table, html
from dash.dependencies import Input, Output, State
# Dataframe imports
import pandas as pd
df = pd.read_excel('final_buysell_preds.xls')

app = Dash(__name__)
# HTML layout
# A file upload is at the top
# a dynamic table is at the bottom.
app.layout = html.Div([
    dash_table.DataTable(
        id='computed-table',
        columns=[
            {'name': 'Capital', 'id': 'capital'},
            {'name': 'KKM GAIN', 'id': 'kkm'},
            {'name': 'Normalized Capital', 'id': 'ncapital'},
            {'name': 'Capital Gain/Loss', 'id': 'gainloss'},
            {'name': 'Capital Gain/Loss Margin', 'id': 'GLmargin'}
        ],
        data=[{'capital': (i+1)*10000} for i in range(6)],
        editable=True,
    ),
])

# callback for the table 
@app.callback(
    Output('computed-table', 'data'),
    Input('computed-table', 'data_timestamp'),
    State('computed-table', 'data'))

# Method: update_columns()
# Updates each column according the user input on the capital colum in row-wise.
# Returns an updates HTML table.
# in calculations it uses dataframe at the top for std() calculations and USD buy/sell predictions.
# Parameters:
#   timestamps - timestamp
#   rows - rows of the table
def update_columns(timestamp, rows):
    for row in rows:
        kkm = 0.14
        interest = 0.84/4
        usd_volatility = df['sell'].std()
        try:
            row['kkm'] = float(row['capital']) * (kkm/4+1)
            row['ncapital'] = float(row['capital']) * (interest+1)
            row['gainloss'] = (float(row['capital']) * (kkm/4+1)) - (float(row['capital']) * (interest+1))
            row['GLmargin'] = ((float(row['capital']) * (kkm/4+1)) - (float(row['capital']) * (interest+1))) * usd_volatility *0.05
        except:
            row['kkm'] = 'NA'
            row['ncapital'] = 'NA'
            row['gainloss'] = 'NA'
            row['GLmargin'] = 'NA'
    return rows

# yes main is here :)
if __name__ == '__main__':
    app.run_server(debug=True)
