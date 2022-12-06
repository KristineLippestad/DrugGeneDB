from dash import Dash, html, dcc, Input, Output, exceptions, no_update
import plotly.express as px
import dash_cytoscape as cyto

import pandas as pd
import sqlite3
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

create_connection('DrugTargetInteractionDB.db')

app = Dash(__name__)

colors = {
    'background': '#E5F4FA',
    'text': '#000000'
}

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
        html.Label('Kd slider'),
        dcc.Slider(
            0,
            4,
            0.1,
            id='kd--slider',
            marks={i: '{}'.format(10 ** i) for i in range(5)},
            value=0,
            tooltip={'placement': 'bottom', 'always_visible': True},
            updatemode='drag'
        ),

        html.Div(id='kd-output-container', style={'margin-top': 20}),

        html.Br(),
        html.Label('Ki slider'),
        dcc.Slider(
            0,
            4,
            0.1,
            id='ki--slider',
            marks={i: '{}'.format(10 ** i) for i in range(5)},
            value=0,
            tooltip={'placement': 'bottom', 'always_visible': True},
            updatemode='drag'
        ),

        html.Div(id='ki-output-container', style={'margin-top': 20}),

        html.Br(),
        html.Label(u'IC\u2085\u2080 slider'),
        dcc.Slider(
            0,
            4,
            0.1,
            id='ic50--slider',
            marks={i: '{}'.format(10 ** i) for i in range(5)},
            value=0,
            tooltip={'placement': 'bottom', 'always_visible': True},
            updatemode='drag'
        ),

        html.Div(id='ic50-output-container', style={'margin-top': 20})],  
        style={'margin-bottom': -80, 'margin-top': 120, 'margin-left': 80, 'padding': 10, 'width':600, 'borderRadius': '10px', 'backgroundColor': colors['background']}),

    html.Div([
        html.H3('Experimental conditions'),

        'Temperature: ',
        dcc.Input(id='temp-input', value='initial value', type='text'),

        html.Br(),
        html.Br(),
        "pH: ",
        dcc.Input(id='ph-input', value='initial value', type='text')
        ], style={'margin-top': 120, 'margin-left': 80, 'padding': 10, 'width':250, 'borderRadius': '10px', 'backgroundColor': colors['background']}), # H Head line (number indicates size (1-6))),

    html.Div([

        html.Div([
            html.Button("Download drug panel", id="btn_drugpanel"), 
            dcc.Download(id="download-text-index")
            ], style={'padding-left': '40%', 'margin-top': -92}),
        html.Div([
        html.Br(),
        html.Div(id='drugPanel-output', style = {'margin-left': -50, 'width':600})])

    ],style={'margin-top': -530, 'margin-left': 750,'width':480, 'padding':100, 'borderRadius': '10px','backgroundColor': colors['background']}), #'margin-top': -800, 'padding': 100, 'padding-left': '21.5%', 'width':250, 

    html.Div([
    
    html.Div([dcc.RadioItems(id = 'selectedDrugs-output')
    ]),

    html.Div([
    cyto.Cytoscape(
        id='cytoscape-drugTargetNet',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '400px'}, 
        
    )])
], style={'margin-top': 40, 'margin-left': 750, 'padding': 10, 'width':660, 'borderRadius': '10px', 'backgroundColor': colors['background']}),
])

#Every callback needs at least one oínput and one output
#Every single pair of output can only have one callback
@app.callback(
    [Output(component_id='kd-output-container', component_property='children'),
    Output(component_id='ki-output-container', component_property='children'),
    Output(component_id='ic50-output-container', component_property='children'),
    Output(component_id='selectedDrugs-output', component_property='options'),
    Output(component_id='drugPanel-output', component_property='children'),
    Output(component_id='cytoscape-drugTargetNet', component_property='elements')
    ], #Multiple outputs muse be placed inside a list, Output is the children property of the component with the ID 'graph-with-slicer'
    [Input(component_id='drugID-dropdown', component_property='value'), 
    Input(component_id='kd--slider', component_property='value'), #multiple inputs must also be inside a list
    Input(component_id='ki--slider', component_property='value'),
    Input(component_id='ic50--slider', component_property='value'),
    Input(component_id='selectedDrugs-output', component_property='value')] #need to return as many figures as you have inputs
     #State can be used if a button should be clicked to update a figure (might be used for pH, temp and to download drugpanel)
    #, prevent_initial-call=True #Doesn't trigger all call back when the page is refreshed.
    )

def update_figure(drugID_list, kd_value, ki_value, ic50_value, selectedDrug): # Input referes to component property of input, same as saying that the input is the value declared in app.layout. 
    kd = transform_value(kd_value)
    ki = transform_value(ki_value)
    ic50 = transform_value(ic50_value)
    print(kd, ki, ic50)
    
    if len(drugID_list) == 0:
        return 'Threshold selected for Kd: "{}"'.format(kd), 'Threshold selected for Ki: "{}"'.format(ki), u'Threshold selected for IC\u2085\u2080: "{}"'.format(ic50), no_update, no_update, no_update, no_update
    
    elif len(drugID_list) > 0 and selectedDrug == None:
        #remember to make a copy of the df if you change it
        dp = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50)
        netOptions = radioItemsOptions(drugID_list)
        return 'Threshold selected for Kd: "{}"'.format(kd), 'Threshold selected for Ki: "{}"'.format(ki), u'Threshold selected for IC\u2085\u2080: "{}"'.format(ic50), netOptions, dp, no_update
    else: 
        print(f'ID user chose: {selectedDrug}')
        #remember to make a copy of the df if you change it
        dp = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50)
        netOptions = radioItemsOptions(drugID_list)
        print(f'Selected drug {selectedDrug}')
        netElements = drugTargetNet(selectedDrug, kd_limit = kd, ki_limit = ki, ic50_limit = ic50)
        return 'Threshold selected for Kd: "{}"'.format(kd), 'Threshold selected for Ki: "{}"'.format(ki), u'Threshold selected for IC\u2085\u2080: "{}"'.format(ic50), netOptions, dp, netElements

def radioItemsOptions(drugID_list):
    options = [{'label': x, 'value': x} for x in drugID_list]
    return options

def drugTargetNet(selectedDrug, kd_limit = None, ki_limit = None, ic50_limit = None):
    
    print(f'kd {kd_limit}, ki {ki_limit}, ic50 {ic50_limit}')
    # Network for selected drug where node size depends on binding affinity
    targets = targetList(selectedDrug, kd_limit, ki_limit, ic50_limit)
    #elements = [{'data': {'id': 'drug', 'label': selectedDrug}, 'position': {'x': 50, 'y': 50}, 'size':50}]
    elements = [{'data': {'id': 'drug', 'label': selectedDrug}, 'position': {'x': 50, 'y': 50}}]
    a = 200
    for i in targets:
        #elements.append({'data': {'id': i, 'label': i}, 'position': {'x': 200, 'y': 200}, 'size':70}) 
        #elements.append({'data': {'source': 'drug', 'target': i,'label': f'Node {selectedDrug} to {i}'}})
        
        print(f'type {type(i)}')
        print(i)

        targetData = {}
        targetData['id'] = str(i)
        targetData['label'] = str(i)

        print(targetData)

        targetPosition = {}
        targetPosition['x'] = a
        targetPosition['y'] = 200
        a += 40

        print(targetPosition)

        targetDict = {}
        targetDict['data'] = targetData
        targetDict['position'] = targetPosition

        print(targetDict)

        elements.append(targetDict) 

        edgeData = {}
        edgeData['source'] = 'drug'
        edgeData['target'] = str(i)
        edgeData['label'] = f'Node {selectedDrug} to {str(i)}'

        edgeDict = {}
        edgeDict['data'] = edgeData

        elements.append(edgeDict)
    
    print(elements)
    
    '''
    elements=[
        {'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 75, 'y': 75}},
        {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 200, 'y': 200}},
        {'data': {'source': 'one', 'target': 'two'}}
    ]       
    '''
    return elements


def targetProfileBA(id_list, kd_limit = None, ki_limit = None, ic50_limit = None):
    """Retrieve target profiles for a list of drugs with measured binding affinities below set limits and write them to a drug panel file. 
    :param db_file: database db_file, file_name: name for drugpanel file, id_list: list of drug IDs, kd_limit: Upper limit for kd value for binding affinity, ki_limit: Upper limit for ki value for binding affinity, ic50_limit: Upper limit for ic50 value for binding affinity. 
    """

    complete_dp = ""
    for i in id_list:
        
        targets = targetList(i, kd_limit, ki_limit, ic50_limit)
    
        if len(targets) > 0: 
            dp = i + "\t" + "inhibits" + "\t" + ",\t".join(sorted(set(targets))) #+ "\n" # comma must be removed if this should be used to make the drugtarget panel
            complete_dp = complete_dp + "\n" + dp

        targets.clear()

    print(complete_dp)
    
    return complete_dp

def targetList(drugID, kd_limit = None, ki_limit = None, ic50_limit = None):
    create_connection('DrugTargetInteractionDB.db')
    frames = []
    if kd_limit != None:
        cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  Kd_max <= ?", (drugID, kd_limit))
        df1 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
        frames.append(df1)

    if ki_limit != None: 
        cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  Ki_max <= ?", (drugID, ki_limit))
        df2 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
        frames.append(df2)

    if ic50_limit: 
        cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  IC50_max <= ?", (drugID, ic50_limit))
        df3 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
        frames.append(df3)
            
    dp_df = pd.concat(frames, ignore_index=True)

    targetList = []
    for ind in dp_df.index:
        targetList.append(dp_df["HGNC"][ind])

    con.close()

    return targetList

def transform_value(value):
    if value == 0:
        return 0
    else: 
        return round(10 ** value, 2)

if __name__ == '__main__':
    app.run_server(debug=True)