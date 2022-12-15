from dash import Dash, html, dcc, Input, Output, exceptions, no_update
from dash.exceptions import PreventUpdate
import plotly.express as px
import dash_cytoscape as cyto

import pandas as pd
import sqlite3
import threading
import math
from aifc import Error

# https://towardsdatascience.com/dashing-through-christmas-songs-using-dash-and-sql-34ef2eb4d0cb
# https://plotly.com/python/

#Connect to the database
def create_connection(db_file):
    """Create a database connection to the SQLite database given by the db_file
    :param db_file: database db_file
    :return: Connection object or None"""

    global con
    global cursor

    try:
        con = sqlite3.connect(db_file)
        cursor = con.cursor()
        print("Successfully connected to SQLite")
    except Error as e:
        print(e)
        print("ERROR")

    return con

app = Dash(__name__)

lock = threading.Lock()

colors = {
    'background': '#E5F4FA',
    'text': '#000000'
}

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

default_stylesheet = [
    {
        "selector": "node",
        "style": {
            "width": "mapData(size, 0, 100, 20, 60)",
            "height": "mapData(size, 0, 100, 20, 60)",
            "content": "data(label)",
            "font-size": "12px",
            "text-valign": "center",
            "text-halign": "center",
        }
    },

    {
        'selector': '.darkGrey',
        'style': {
            'background-color': '#565656',
            'line-color': '#565656'
        }
    },
]

create_connection('DrugTargetInteractionDB.db')
drug_query = pd.read_sql_query("SELECT DISTINCT DrugID From MeasuredFor", con) # Only drugIDs with associated binding affinity values are included.
con.close()

drug_df = pd.DataFrame(drug_query, columns = ['DrugID'])

app.layout = html.Div([
    html.Div(children=[
    html.H1( 
        children='Drug Target Profile Generated from Binding Affinity Values',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'height':5, 'width':1000 
        })
    ]), # H Head line (number indicates size (1-6))

    html.Div(children=[
        html.Label('Select drug IDs'),
        html.Br(),
        dcc.Dropdown(drug_df['DrugID'].unique(),
                     multi=True, # If true, the user can select multiple values
                     #value = [],
                     id='drugID-dropdown'), #list er ikke riktig
     ], style={'margin-bottom': -80, 'margin-top': 70, 'margin-left': 80, 'padding': 10, 'width':1330, 'borderRadius': '10px', 'backgroundColor': colors['background']}),

    html.Div([
        html.H3('Binding Affinity Thresholds'),
        html.Label(['K', html.Sub('d'), ' slider']),
        dcc.Slider(
            0,
            4,
            0.1,
            id='kd--slider',
            marks={i: '{}'.format(10 ** i) for i in range(5)},
            value=0,
            updatemode='drag'
        ),

        html.Div(id='kd-output-container', style={'margin-top': 20}),

        html.Br(),
        html.Label(['K', html.Sub('i'), ' slider']),
        dcc.Slider(
            0,
            4,
            0.1,
            id='ki--slider',
            marks={i: '{}'.format(10 ** i) for i in range(5)},
            value=0,
            updatemode='drag'
        ),

        html.Div(id='ki-output-container', style={'margin-top': 20}),

        html.Br(),
        html.Label(['IC', html.Sub('50'), ' slider']),
        dcc.Slider(
            0,
            4,
            0.1,
            id='ic50--slider',
            marks={i: '{}'.format(10 ** i) for i in range(5)},
            value=0,
            updatemode='drag'
        ),

        html.Div(id='ic50-output-container', style={'margin-top': 20})],  
        style={'margin-bottom': -80, 'margin-top': 120, 'margin-left': 80, 'padding': 10, 'width':600, 'borderRadius': '10px', 'backgroundColor': colors['background']}),

    html.Div([
        html.H3('Experimental conditions'),

        'Temperature: ',
        dcc.Input(id='temp-input', type='number'),

        html.Br(),
        html.Br(),
        "pH: ",
        dcc.Input(id='ph-input', type='number')
        ], style={'margin-top': 120, 'margin-left': 80, 'padding': 10, 'width':250, 'borderRadius': '10px', 'backgroundColor': colors['background']}), # H Head line (number indicates size (1-6))),

    html.Div([
    html.Div([
            'Filename: ',
            dcc.Input(id='filename-input', value='drugPanel', type='text'),
            html.Button("download-drug-panel", id='btn_drugpanel'), 
            dcc.Store(id='intermediate-text'),
            dcc.Download(id="download-text")
            ], style={'margin-top': -642, 'margin-left': 318}),
    
    html.Div([
        html.Br(),
        html.P(id='drugPanel-output', style = {'margin-left': -50, 'margin-top': -80, 'width':600})
    ], style={'margin-top': 5, 'margin-left': -20,'width':490, 'padding':100, 'borderRadius': '10px','backgroundColor': colors['background']}), #'margin-top': -800, 'padding': 100, 'padding-left': '21.5%', 'width':250, 
    
    html.Div([
    html.Div([dcc.RadioItems(id = 'selectedDrugs-output')
    ], style = {'margin-left': -50, 'margin-top': -70, 'width':600}),

    html.Div([
        cyto.Cytoscape(
            id='cytoscape-drugTargetNet',
            layout={'name': 'preset'},
            stylesheet=default_stylesheet,
        ),
        html.P(id='cytoscape-tapNodeData-output'),
    ])], style={'margin-top': 40, 'margin-left': -20,'width':490, 'height':520, 'padding':100, 'borderRadius': '10px','backgroundColor': colors['background']})
], style={'margin-top': 20, 'margin-left': 750}),
])

#Every callback needs at least one oínput and one output
#Every single pair of output can only have one callback
@app.callback(
    [Output(component_id='kd-output-container', component_property='children'),
    Output(component_id='ki-output-container', component_property='children'),
    Output(component_id='ic50-output-container', component_property='children'),
    Output(component_id='selectedDrugs-output', component_property='options'),
    Output(component_id='drugPanel-output', component_property='children'),
    Output(component_id='cytoscape-drugTargetNet', component_property='elements'),
    Output('intermediate-text', 'data')], #Multiple outputs muse be placed inside a list, Output is the children property of the component with the ID 'graph-with-slicer'
    [Input(component_id='drugID-dropdown', component_property='value'), 
    Input(component_id='kd--slider', component_property='value'), #multiple inputs must also be inside a list
    Input(component_id='ki--slider', component_property='value'),
    Input(component_id='ic50--slider', component_property='value'),
    Input(component_id='temp-input', component_property='value'),
    Input(component_id='ph-input', component_property='value'),
    Input(component_id='selectedDrugs-output', component_property='value')], #need to return as many figures as you have inputs
     #State can be used if a button should be clicked to update a figure (might be used for pH, temp and to download drugpanel)
    #, prevent_initial-call=True #Doesn't trigger all call back when the page is refreshed.
    )

def update_figure(drugID_list, kd_value, ki_value, ic50_value, temp, ph, selectedDrug): # Input referes to component property of input, same as saying that the input is the value declared in app.layout. 
    kd = transform_value(kd_value)
    ki = transform_value(ki_value)
    ic50 = transform_value(ic50_value)
    
    if str(type(drugID_list)) == "<class 'NoneType'>":
        return 'Threshold selected for Kd: {}'.format(kd), 'Threshold selected for Ki: {}'.format(ki), u'Threshold selected for IC\u2085\u2080: {}'.format(ic50), no_update, no_update, no_update, no_update
    
    elif len(drugID_list) > 0 and selectedDrug == None:
        dp, dpText = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        netOptions = radioItemsOptions(drugID_list)
        return 'Threshold selected for Kd: {}'.format(kd), 'Threshold selected for Ki: {}'.format(ki), u'Threshold selected for IC\u2085\u2080: {}'.format(ic50), netOptions, dp, no_update, dpText
    else: 
        dp, dpText = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        netOptions = radioItemsOptions(drugID_list)
        netElements = drugTargetNet(selectedDrug, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        return 'Threshold selected for Kd: {}'.format(kd), 'Threshold selected for Ki: {}'.format(ki), u'Threshold selected for IC\u2085\u2080: {}'.format(ic50), netOptions, dp, netElements, dpText

def radioItemsOptions(drugID_list):
    options = [{'label': x, 'value': x} for x in drugID_list]
    return options

def drugTargetNet(selectedDrug, kd_limit = None, ki_limit = None, ic50_limit = None, Temp = None, pH = None):

    # Network for selected drug where node size depends on binding affinity
    targets = sorted(targetList(selectedDrug, kd_limit, ki_limit, ic50_limit, pH, Temp))
    #elements = [{'data': {'id': 'drug', 'label': selectedDrug}, 'position': {'x': 50, 'y': 50}, 'size':50}]
    elements = [{'data': {'id': 'drug', 'label': selectedDrug}, 'position': {'x': 50, 'y': 50}}]
    a = 200
    b = 200

    for i in targets:

        min_value, max_value = minMaxValues(selectedDrug, i, kd_limit, ki_limit, ic50_limit, Temp, pH)

        targetData = {}
        targetData['id'] = i
        targetData['label'] = i
        targetData['size'] = min_value*100

        targetPosition = {}
        targetPosition['x'] = a
        targetPosition['y'] = b
        a += 40
        b -= 50

        targetDict = {}
        targetDict['data'] = targetData
        targetDict['position'] = targetPosition

        if min_value != max_value:
            targetDict['classes'] = 'darkGrey'
            
        elements.append(targetDict) 

        edgeData = {}
        edgeData['source'] = 'drug'
        edgeData['target'] = i
        edgeData['label'] = f'Node {selectedDrug} to {i}'

        edgeDict = {}
        edgeDict['data'] = edgeData

        elements.append(edgeDict)
        
    return elements
    


def minMaxValues(selectedDrug, i, kd_limit, ki_limit, ic50_limit, temp, pH):

    # add WHERE Kd_max > kd_limit and so on 
    # add mode (typetall) https://www.geeksforgeeks.org/find-mean-mode-sql-server/
    try:

        create_connection('DrugTargetInteractionDB.db')
        
        lock.acquire(True)

        min_values = []
        max_values = []

        if temp != None and pH == None:
            cursor.execute("SELECT MIN(Kd_max), MAX(Kd_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ? and Temperature = ?", (selectedDrug, i, kd_limit, temp))
            kd_df = pd.DataFrame(cursor.fetchall())
            kd_min = kd_df[0][0]
            kd_max = kd_df[1][0]

            if kd_min != None: 
                min_values.append(float(kd_min))

            if kd_max != None: 
                max_values.append(float(kd_max))

            cursor.execute("SELECT MIN(Ki_max), MAX(Ki_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and Temperature = ?", (selectedDrug, i, ki_limit, temp))
            ki_df = pd.DataFrame(cursor.fetchall())
            ki_min = ki_df[0][0]
            ki_max = ki_df[1][0]              
            
            if ki_min != None:
                min_values.append(float(ki_min))

            if ki_max != None:
                max_values.append(float(ki_max))

            cursor.execute("SELECT MIN(IC50_max), MAX(IC50_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ? and Temperature = ?", (selectedDrug, i, ic50_limit, temp))
            ic50_df = pd.DataFrame(cursor.fetchall())
            ic50_min = ic50_df[0][0]
            ic50_max = ic50_df[1][0]
            
            if ic50_min != None: 
                min_values.append(float(ic50_min))

            if ic50_max != None: 
                max_values.append(float(ic50_max)) 

        elif temp == None and pH != None:
            cursor.execute("SELECT MIN(Kd_max), MAX(Kd_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? Kd_max <= ? and pH = ?", (selectedDrug, i, kd_limit, pH))
            kd_df = pd.DataFrame(cursor.fetchall())
            kd_min = kd_df[0][0]
            kd_max = kd_df[1][0]

            if kd_min != None: 
                min_values.append(float(kd_min))

            if kd_max != None: 
                max_values.append(float(kd_max))

            cursor.execute("SELECT MIN(Ki_max), MAX(Ki_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and pH = ?", (selectedDrug, i, ki_limit, pH))
            ki_df = pd.DataFrame(cursor.fetchall())
            ki_min = ki_df[0][0]
            ki_max = ki_df[1][0]              
            
            if ki_min != None:
                min_values.append(float(ki_min))

            if ki_max != None:
                max_values.append(float(ki_max))

            cursor.execute("SELECT MIN(IC50_max), MAX(IC50_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ? and pH = ?", (selectedDrug, i, ic50_limit, pH))
            ic50_df = pd.DataFrame(cursor.fetchall())
            ic50_min = ic50_df[0][0]
            ic50_max = ic50_df[1][0]
            
            if ic50_min != None: 
                min_values.append(float(ic50_min))

            if ic50_max != None: 
                max_values.append(float(ic50_max))     

        elif temp != None and pH != None:

            cursor.execute("SELECT MIN(Kd_max), MAX(Kd_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ? and Temperature = ? and pH = ?", (selectedDrug, i, kd_limit, temp, pH))
            kd_df = pd.DataFrame(cursor.fetchall())
            kd_min = kd_df[0][0]
            kd_max = kd_df[1][0]

            if kd_min != None: 
                min_values.append(float(kd_min))

            if kd_max != None: 
                max_values.append(float(kd_max))

            cursor.execute("SELECT MIN(Ki_max), MAX(Ki_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and Temperature = ? and pH = ?", (selectedDrug, i, ki_limit, temp, pH))
            ki_df = pd.DataFrame(cursor.fetchall())
            ki_min = ki_df[0][0]
            ki_max = ki_df[1][0]              
            
            if ki_min != None:
                min_values.append(float(ki_min))

            if ki_max != None:
                max_values.append(float(ki_max))

            cursor.execute("SELECT MIN(IC50_max), MAX(IC50_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  HGNC = ? and IC50_max <= ? and Temperature = ? and pH = ?", (selectedDrug, i, ic50_limit, temp, pH))
            ic50_df = pd.DataFrame(cursor.fetchall())
            ic50_min = ic50_df[0][0]
            ic50_max = ic50_df[1][0]
            
            if ic50_min != None: 
                min_values.append(float(ic50_min))

            if ic50_max != None: 
                max_values.append(float(ic50_max))        
        
        else: 

            cursor.execute("SELECT MIN(Kd_max), MAX(kd_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ?", (selectedDrug, i, kd_limit))
            kd_df = pd.DataFrame(cursor.fetchall())
            kd_min = kd_df[0][0]
            kd_max = kd_df[1][0]

            if kd_min != None: 
                min_values.append(float(kd_min))

            if kd_max != None: 
                max_values.append(float(kd_max))

            cursor.execute("SELECT MIN(Ki_max), MAX(Ki_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ?", (selectedDrug, i, ki_limit))
            ki_df = pd.DataFrame(cursor.fetchall())
            ki_min = ki_df[0][0]
            ki_max = ki_df[1][0]              
            
            if ki_min != None:
                min_values.append(float(ki_min))

            if ki_max != None:
                max_values.append(float(ki_max))

            cursor.execute("SELECT MIN(IC50_max), MAX(IC50_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ?", (selectedDrug, i, ic50_limit))
            ic50_df = pd.DataFrame(cursor.fetchall())
            ic50_min = ic50_df[0][0]
            ic50_max = ic50_df[1][0]
            
            if ic50_min != None: 
                min_values.append(float(ic50_min))

            if ic50_max != None: 
                max_values.append(float(ic50_max))                
            
        con.close()
        
        min_value = min(min_values)
        max_value = max(max_values)

        return min_value, max_value

    finally:
        lock.release()


def targetProfileBA(id_list, kd_limit = None, ki_limit = None, ic50_limit = None, Temp = None, pH = None):
    """Retrieve target profiles for a list of drugs with measured binding affinities below set limits and write them to a drug panel file. 
    :param db_file: database db_file, file_name: name for drugpanel file, id_list: list of drug IDs, kd_limit: Upper limit for kd value for binding affinity, ki_limit: Upper limit for ki value for binding affinity, ic50_limit: Upper limit for ic50 value for binding affinity. 
    """

    complete_dp = []

    dpText = "#Name\tTarget:\n"


    for i in id_list:
        
        tList = targetList(i, kd_limit, ki_limit, ic50_limit, pH, Temp)
    
        if len(tList) > 0: 

            dp = f'{i} inhibits {", ".join(sorted(set(tList)))}'
            complete_dp.append(dp)
            complete_dp.append(html.Br())

            dpText = dpText + i + '\tinhibits\t' + '\t'.join(sorted(set(tList))) + '\n'

        tList.clear()
    
    return complete_dp, dpText

def targetList(drugID, kd_limit, ki_limit, ic50_limit, pH, temp):
    try:

        create_connection('DrugTargetInteractionDB.db')
        
        lock.acquire(True)

        if temp != None and pH == None:

            cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and Temperature = ? and (Kd_max <= ? OR Ki_max <= ? OR IC50_max <= ?)", (drugID, temp, kd_limit, ki_limit, ic50_limit))
            df = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
        
        elif pH != None and temp == None: 
            
            cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and pH = ? and (Kd_max <= ? OR Ki_max <= ? OR IC50_max <= ?)", (drugID, pH, kd_limit, ki_limit, ic50_limit))
            df = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
        
        elif pH != None and temp != None: 
            
            cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and Temperature = ? and pH = ? and (Kd_max <= ? OR Ki_max <= ? OR IC50_max <= ?)", (drugID, temp, pH, kd_limit, ki_limit, ic50_limit))
            df = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
        
        else:
        
            cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and (Kd_max <= ? OR Ki_max <= ? OR IC50_max <= ?)", (drugID, kd_limit, ki_limit, ic50_limit))
            df = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])

        targetList = []

        for ind in df.index:
            targetList.append(df["HGNC"][ind])

        con.close()

        return targetList
    
    finally:
        lock.release()

def transform_value(value):
    if value == 0:
        return 0
    else: 
        return round(10 ** value, 2)

@app.callback(Output('cytoscape-tapNodeData-output', 'children'),
              Input('selectedDrugs-output', 'value'),
              Input('cytoscape-drugTargetNet', 'tapNodeData'),

              prevent_initial_call=True)

def displayTapNodeData(drug, data):
    if data:

        target = data['id']

        return f'Lowest binding affinity measured between {drug} and {target}: {data["size"]/100} nM'

        

@app.callback(
    Output("download-text", "data"),
    Output("btn_drugpanel", "n_clicks"),
    Input("btn_drugpanel", "n_clicks"),
    Input('intermediate-text', 'data'),
    Input('filename-input', 'value'),
    prevent_initial_call=True,
)

def func(n_clicks, intText, name):
    if n_clicks is None:
        raise PreventUpdate
    else:
        n_clicks = None
        return dict(content=intText, filename=name), n_clicks

if __name__ == '__main__':
    app.run_server(debug=True)