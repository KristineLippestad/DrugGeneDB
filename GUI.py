from dash import Dash, html, dcc, Input, Output, exceptions, no_update
from dash.exceptions import PreventUpdate
import plotly.express as px
import dash_cytoscape as cyto

import pandas as pd
import sqlite3
import threading
from aifc import Error
from scipy.stats import sem

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
        con = sqlite3.connect(db_file, check_same_thread=False)
        cursor = con.cursor()
        print("Successfully connected to SQLite")
    except Error as e:
        print(e)
        print("ERROR")

    return con

app = Dash(__name__)

# Implement a primitive lock object. 
lock = threading.Lock()


# Colour choices
colors = {
    'background': '#E5F4FA',
    'text': '#000000'
}

# Set style for app
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll', 
        'display':'inline-block'
    }
}

# Stylesheet for cytoscape networks
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

# Select options for selected drug IDs 
create_connection('/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db')
drug_df = pd.read_sql_query("SELECT DISTINCT Drug.DrugID, DrugName From Drug INNER JOIN MeasuredFor ON Drug.DrugID = MeasuredFor.DrugID", con) # Only drugIDs with associated binding affinity values are included.
drugList = []
for ind in drug_df.index: 
    d = f"{drug_df['DrugName'][ind]}: {drug_df['DrugID'][ind]}"
    drugList.append(d)
con.close()

create_connection('/Users/kristinelippestad/Dokumenter/Master/DrugTargetInteractionDB.db')

#drug_df = pd.DataFrame(drug_query, columns = ['DrugID'])

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

    # Selection of drug IDs 
    html.Div(children=[
        html.Label('Select drug IDs'),
        html.Br(),
        dcc.Dropdown( #drug_df['DrugID'].unique(),
                     drugList,
                     multi=True, # If true, the user can select multiple values
                     #value = [],
                     id='drugID-dropdown'), #list er ikke riktig
     ], style={'margin-bottom': -80, 'margin-top': 70, 'margin-left': 80, 'padding': 10, 'width':1330, 'borderRadius': '10px', 'backgroundColor': colors['background']}),

    # Settings for binding affinitiy thresholds
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

    # Settings for experimental conditions
    html.Div([
        html.H3('Experimental conditions'),

        'Temperature: ',
        dcc.Input(id='temp-input', type='number'),

        html.Br(),
        html.Br(),
        "pH: ",
        dcc.Input(id='ph-input', type='number')
        ], style={'margin-top': 120, 'margin-left': 80, 'padding': 10, 'width':250, 'borderRadius': '10px', 'backgroundColor': colors['background']}), # H Head line (number indicates size (1-6))),

    # Downlowd drug panel 
    html.Div([
    html.Div([
            'Filename: ',
            dcc.Input(id='filename-input', value='drugPanel', type='text'),
            html.Button("download-drug-panel", id='btn_drugpanel'), 
            dcc.Store(id='intermediate-text'),
            dcc.Download(id="download-text")
            ], style={'margin-top': -642, 'margin-left': 295}),
    
    # Show drug panel
    html.Div([
        html.H3('Drug Panel', style = {'margin-left': -75, 'margin-top': -80, 'width':600}),
        html.Br(),
        html.P(id='drugPanel-output', style = {'margin-left': -75, 'margin-top': -30, 'width':600})
    ], style={'margin-top': 5, 'margin-left': -20,'width':490, 'padding':100, 'borderRadius': '10px','backgroundColor': colors['background']}), #'margin-top': -800, 'padding': 100, 'padding-left': '21.5%', 'width':250, 
    
    # Drug options
    html.Div([
        html.H3('Drug Target Network', style = {'margin-left': -75, 'margin-top': -80, 'width':600}),
        html.P("The figure displays the selected drug and it's associated targets. Node size is determined by the lowest binding affinity value measured between the drug target pair. Dark grey node colour indicates that multiple binding affinity measurments are stored for the drug target pairs.", 
        style = {'margin-left': -75, 'margin-top': 10, 'width':600}),
        html.Div([dcc.RadioItems(id = 'selectedDrugs-output')
        ], style = {'margin-left': -75, 'margin-top': 10, 'width':490}),
    
    # Network dispalying a selected drug and it's target profile 
    html.Div([
        cyto.Cytoscape(
            id='cytoscape-drugTargetNet',
            layout={'name': 'preset'},
            stylesheet=default_stylesheet,
        ),
        html.P(id='cytoscape-tapNodeData-output'),
    ])], style={'margin-top': 40, 'margin-left': -20,'width':490, 'height':650, 'padding':100, 'borderRadius': '10px','backgroundColor': colors['background']}),
    
    # Selection of drugs and comparison of the mutual targets
    html.Div([
        html.H3('Shared Targets', style = {'margin-left': -75, 'margin-top': -80, 'width':600}),
        html.P('The figure display the targets that are shared between the selected drugs.', style = {'margin-left': -75, 'margin-top': 10, 'width':600}),
        dcc.Checklist(id = 'comparedDrugs-output', inline = True, style={'margin-left': -75, 'margin-top': 10, 'width':600}),
        html.Div([
        cyto.Cytoscape(
            id='cytoscape-mutualTargetNet',
            layout={'name': 'preset'},
            stylesheet=default_stylesheet,
        )]),
        html.Div(id='mutualTargets-output-container', style={'margin-left': -75, 'margin-top': 20, 'width':600}),
    ], style = {'margin-top': 40, 'margin-left': -20,'width':490, 'padding':100, 'borderRadius': '10px','backgroundColor': colors['background']}), 
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
    Output('intermediate-text', 'data'),
    Output(component_id='comparedDrugs-output', component_property='options'),
    Output(component_id='mutualTargets-output-container', component_property='children'),
    Output(component_id='cytoscape-mutualTargetNet', component_property='elements')], #Multiple outputs must be placed inside a list, Output is the children property of the component with the ID 'graph-with-slicer'
    [Input(component_id='drugID-dropdown', component_property='value'), 
    Input(component_id='kd--slider', component_property='value'), #multiple inputs must also be inside a list
    Input(component_id='ki--slider', component_property='value'),
    Input(component_id='ic50--slider', component_property='value'),
    Input(component_id='temp-input', component_property='value'),
    Input(component_id='ph-input', component_property='value'),
    Input(component_id='selectedDrugs-output', component_property='value'),
    Input(component_id='comparedDrugs-output', component_property='value')] #need to return as many figures as you have inputs
     #State can be used if a button should be clicked to update a figure (might be used for pH, temp and to download drugpanel)
    #, prevent_initial-call=True #Doesn't trigger all call back when the page is refreshed.
    )


def update_figure(drug_list, kd_value, ki_value, ic50_value, temp, ph, selectedDrug, comparedDrugs): # Input referes to component property of input, same as saying that the input is the value declared in app.layout. 
    """Callback function that updates the figures when a value is altered
    :param drugID_list: selected drug IDs, kd_value: selected kd threshold, ki_value: selected ki threshold, ic50_value: selected ic50 threshold, 
    temp: temperature selected for experimental conditions, ph: pH selected for experimental conditions, selectedDrug: drug selected for display of drug target network, comparedDrugs: drugs selected for comparison of targets
    :return: Construction of figure objects that are returned to the Dash application"""

    kd = transform_value(kd_value)
    ki = transform_value(ki_value)
    ic50 = transform_value(ic50_value)

    drugID_list = drugList(drug_list)

    # No drugs are selected
    if str(type(drug_list)) == "<class 'NoneType'>":
        return 'Threshold selected for Kd: {} \u03BCM'.format(kd), 'Threshold selected for Ki: {} \u03BCM'.format(ki), u'Threshold selected for IC\u2085\u2080: {} \u03BCM'.format(ic50), no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    # Drugs are selected
    elif len(drugID_list) > 0 and selectedDrug == None and comparedDrugs == None:
        dp, dpText = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        netOptions = radioItemsOptions(drugID_list)
        checkOptions = checklistOptions(drugID_list)
        return 'Threshold selected for Kd: {} \u03BCM'.format(kd), 'Threshold selected for Ki: {} \u03BCM'.format(ki), u'Threshold selected for IC\u2085\u2080: {} \u03BCM'.format(ic50), netOptions, dp, no_update, dpText, checkOptions, no_update, no_update
    
    # The drug that will be displayed in a network with it's targets is selected
    elif len(drugID_list) > 0 and selectedDrug != None and comparedDrugs == None:
        dp, dpText = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        netOptions = radioItemsOptions(drugID_list)
        checkOptions = checklistOptions(drugID_list)
        netElements = drugTargetNet(selectedDrug, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        return 'Threshold selected for Kd: {} \u03BCM'.format(kd), 'Threshold selected for Ki: {} \u03BCM'.format(ki), u'Threshold selected for IC\u2085\u2080: {} \u03BCM'.format(ic50), netOptions, dp, netElements, dpText, checkOptions, no_update, no_update

    # Drugs are selected to be compared to find shared targets
    elif len(drugID_list) > 0 and selectedDrug == None and comparedDrugs != None:
        dp, dpText = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        netOptions = radioItemsOptions(drugID_list)
        checkOptions = checklistOptions(drugID_list)
        netElements = drugTargetNet(selectedDrug, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        mutual, mutNetElements = mutualTargets(comparedDrugs, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        return 'Threshold selected for Kd: {} \u03BCM'.format(kd), 'Threshold selected for Ki: {} \u03BCM'.format(ki), u'Threshold selected for IC\u2085\u2080: {} \u03BCM'.format(ic50), netOptions, dp, netElements, dpText, checkOptions, mutual, mutNetElements

    # A drug is selected to be displayed in a network with it's targets and drugs are selected to be compared to find shared targets
    else: 
        dp, dpText = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        netOptions = radioItemsOptions(drugID_list)
        checkOptions = checklistOptions(drugID_list)
        netElements = drugTargetNet(selectedDrug, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        mutual, mutNetElements = mutualTargets(comparedDrugs, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        return 'Threshold selected for Kd: {} \u03BCM'.format(kd), 'Threshold selected for Ki: {} \u03BCM'.format(ki), u'Threshold selected for IC\u2085\u2080: {} \u03BCM'.format(ic50), netOptions, dp, netElements, dpText, checkOptions, mutual, mutNetElements

def drugList(drugID_list):
    IDlist = []
    if str(type(drugID_list)) != "<class 'NoneType'>":
        for i in drugID_list:
            a = i.split(': ')
            id = a[1]
            IDlist.append(id)

    return(IDlist)

def radioItemsOptions(drugID_list):
    """Retrieve the selection of drugs that can be compared to find shared targets
    :param drugID_list: selected drug IDs
    :return: radio items for selection of drugs in drug target network box"""

    options = [{'label': x, 'value': x} for x in drugID_list]
    return options

def checklistOptions(drugID_list):
    """Retrieve the selection of drugs that can be choosen to be displayed in a network with it's targets
    :param drugID_list: selected drug IDs
    :return: checklist for selection of drugs in shared targets box"""

    options = [{'label': x, 'value': x} for x in drugID_list]
    return options

def mutualTargets(comparedDrugs, kd_limit = None, ki_limit = None, ic50_limit = None, Temp = None, pH = None):
    """Identifies shared targets between selected drugs
    :param comparedDrugs: drugs selected to be compared, kd_limit: selected kd threshold, ki_limit: selected ki threshold, ic50_limit: selected ic50 threshold, 
    temp: temperature selected for experimental conditions, ph: pH selected for experimental conditions
    :return: Text showing the shared genes and network elements to display the result"""

    allTargets = []

    for i in comparedDrugs: 

        targets = sorted(targetList(i, kd_limit, ki_limit, ic50_limit, pH, Temp))

        allTargets = allTargets + targets


    mutualTargets = []

    for j in allTargets:
        x = allTargets.count(j)
        if x > 1 and x == len(comparedDrugs):
            mutualTargets.append(j)
    
    mutual = 'Mutual targets: ' + ', '.join(set(mutualTargets))

    mutualNetElements = mutualTargetsNet(comparedDrugs, set(mutualTargets))

    if len(mutualTargets) > 0:

        return mutual, mutualNetElements

    else:
        return 'No mutual targets', mutualNetElements

def mutualTargetsNet(drugs, targets):
    """Set the elements that are to be included in the network displaying the selected drugs and their shared targets. 
    :param drugs: drugs selected to be compared, targets: targets that are shared between the selected drugs
    :return: network elements"""
    
    elements = []

    x = 50
    y = 0
    
    for i in drugs:

        drugNode = nodeData(i, x, y)
        elements.append(drugNode)

        y += 100

    if len(targets) > 0: 
        for j in targets:

            targetNode = nodeData(j, x, 50)
            elements.append(targetNode)

            x += 50

    for a in drugs:
        for b in targets: 
    
            edgeData = {}
            edgeData['source'] = str(a)
            edgeData['target'] = str(b)
            edgeData['label'] = f'Node {a} to {b}'

            edgeDict = {}
            edgeDict['data'] = edgeData

            elements.append(edgeDict)

    return elements

def nodeData(node, x, y):
    """Write a dictionary with settings for network elements
    :param node: node name, x: node position on x-axis, y: node position on y-axis
    :return: dictionary with settings for the network element"""

    targetData = {}
    targetData['id'] = node
    targetData['label'] = node
    targetData['size'] = 0.1

    targetPosition = {}
    targetPosition['x'] = x
    targetPosition['y'] = y

    targetDict = {}
    targetDict['data'] = targetData
    targetDict['position'] = targetPosition

    return targetDict

def drugTargetNet(selectedDrug, kd_limit = None, ki_limit = None, ic50_limit = None, Temp = None, pH = None):
    """Set the elements that are to be included in the network displaying the selected drug and its targets 
    :param selectedDrug: drug selected to be dispalyed, kd_limit: selected kd threshold, ki_limit: selected ki threshold, ic50_limit: selected ic50 threshold, 
    temp: temperature selected for experimental conditions, ph: pH selected for experimental conditions
    :return: network elements"""

    # Network for selected drug where node size depends on binding affinity
    targets = sorted(targetList(selectedDrug, kd_limit, ki_limit, ic50_limit, pH, Temp))
    elements = [{'data': {'id': 'drug', 'label': selectedDrug}, 'position': {'x': 50, 'y': 50}}]
    a = 200
    b = 200

    for i in targets:

        min_value, max_value = minMaxValues(selectedDrug, i, kd_limit, ki_limit, ic50_limit, Temp, pH)

        targetData = {}
        targetData['id'] = i
        targetData['label'] = i
        targetData['size'] = 100/min_value

        targetPosition = {}
        targetPosition['x'] = a
        targetPosition['y'] = b
        a += 40
        b -= 50

        targetDict = {}
        targetDict['data'] = targetData
        targetDict['position'] = targetPosition

        # Change node colour when different values are measured between the drug and the target. 

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
    


def minMaxValues(selectedDrug, target, kd_limit, ki_limit, ic50_limit, temp, pH):
    """Identify the minimum and maximum value measued between a drug target pair (considering only values measured below the set threshold)
    :param selecteddrugs: drug, target: target, kd_limit: selected kd threshold, ki_limit: selected ki threshold, ic50_limit: selected ic50 threshold, 
    temp: temperature selected for experimental conditions, ph: pH selected for experimental conditions
    :return: minimum and maximum value for measured binding affinity between a drug target pair"""

    # The min and max value is determined by the set thresholds (only measurements below the set threshold are considered)
    # This influence the colourcode

    # add mode (typetall) https://www.geeksforgeeks.org/find-mean-mode-sql-server/

    try:

        #create_connection('DrugTargetInteractionDB.db')
        
        lock.acquire(True)

        min_values = []
        max_values = []

        if temp != None and pH == None:
            cursor.execute("SELECT MIN(Kd_max), MAX(Kd_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ? and Temperature = ?", (selectedDrug, target, kd_limit, temp))
            kd_df = pd.DataFrame(cursor.fetchall())
            kd_min = kd_df[0][0]
            kd_max = kd_df[1][0]

            if kd_min != None: 
                min_values.append(float(kd_min))

            if kd_max != None: 
                max_values.append(float(kd_max))

            cursor.execute("SELECT MIN(Ki_max), MAX(Ki_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and Temperature = ?", (selectedDrug, target, ki_limit, temp))
            ki_df = pd.DataFrame(cursor.fetchall())
            ki_min = ki_df[0][0]
            ki_max = ki_df[1][0]              
            
            if ki_min != None:
                min_values.append(float(ki_min))

            if ki_max != None:
                max_values.append(float(ki_max))

            cursor.execute("SELECT MIN(IC50_max), MAX(IC50_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ? and Temperature = ?", (selectedDrug, target, ic50_limit, temp))
            ic50_df = pd.DataFrame(cursor.fetchall())
            ic50_min = ic50_df[0][0]
            ic50_max = ic50_df[1][0]
            
            if ic50_min != None: 
                min_values.append(float(ic50_min))

            if ic50_max != None: 
                max_values.append(float(ic50_max)) 

        elif temp == None and pH != None:
            cursor.execute("SELECT MIN(Kd_max), MAX(Kd_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? Kd_max <= ? and pH = ?", (selectedDrug, target, kd_limit, pH))
            kd_df = pd.DataFrame(cursor.fetchall())
            kd_min = kd_df[0][0]
            kd_max = kd_df[1][0]

            if kd_min != None: 
                min_values.append(float(kd_min))

            if kd_max != None: 
                max_values.append(float(kd_max))

            cursor.execute("SELECT MIN(Ki_max), MAX(Ki_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and pH = ?", (selectedDrug, target, ki_limit, pH))
            ki_df = pd.DataFrame(cursor.fetchall())
            ki_min = ki_df[0][0]
            ki_max = ki_df[1][0]              
            
            if ki_min != None:
                min_values.append(float(ki_min))

            if ki_max != None:
                max_values.append(float(ki_max))

            cursor.execute("SELECT MIN(IC50_max), MAX(IC50_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ? and pH = ?", (selectedDrug, target, ic50_limit, pH))
            ic50_df = pd.DataFrame(cursor.fetchall())
            ic50_min = ic50_df[0][0]
            ic50_max = ic50_df[1][0]
            
            if ic50_min != None: 
                min_values.append(float(ic50_min))

            if ic50_max != None: 
                max_values.append(float(ic50_max))     

        elif temp != None and pH != None:

            cursor.execute("SELECT MIN(Kd_max), MAX(Kd_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ? and Temperature = ? and pH = ?", (selectedDrug, target, kd_limit, temp, pH))
            kd_df = pd.DataFrame(cursor.fetchall())
            kd_min = kd_df[0][0]
            kd_max = kd_df[1][0]

            if kd_min != None: 
                min_values.append(float(kd_min))

            if kd_max != None: 
                max_values.append(float(kd_max))

            cursor.execute("SELECT MIN(Ki_max), MAX(Ki_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and Temperature = ? and pH = ?", (selectedDrug, target, ki_limit, temp, pH))
            ki_df = pd.DataFrame(cursor.fetchall())
            ki_min = ki_df[0][0]
            ki_max = ki_df[1][0]              
            
            if ki_min != None:
                min_values.append(float(ki_min))

            if ki_max != None:
                max_values.append(float(ki_max))

            cursor.execute("SELECT MIN(IC50_max), MAX(IC50_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  HGNC = ? and IC50_max <= ? and Temperature = ? and pH = ?", (selectedDrug, target, ic50_limit, temp, pH))
            ic50_df = pd.DataFrame(cursor.fetchall())
            ic50_min = ic50_df[0][0]
            ic50_max = ic50_df[1][0]
            
            if ic50_min != None: 
                min_values.append(float(ic50_min))

            if ic50_max != None: 
                max_values.append(float(ic50_max))        
        
        else: 

            cursor.execute("SELECT MIN(Kd_max), MAX(kd_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ?", (selectedDrug, target, kd_limit))
            kd_df = pd.DataFrame(cursor.fetchall())
            kd_min = kd_df[0][0]
            kd_max = kd_df[1][0]

            if kd_min != None: 
                min_values.append(float(kd_min))

            if kd_max != None: 
                max_values.append(float(kd_max))

            cursor.execute("SELECT MIN(Ki_max), MAX(Ki_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ?", (selectedDrug, target, ki_limit))
            ki_df = pd.DataFrame(cursor.fetchall())
            ki_min = ki_df[0][0]
            ki_max = ki_df[1][0]              
            
            if ki_min != None:
                min_values.append(float(ki_min))

            if ki_max != None:
                max_values.append(float(ki_max))

            cursor.execute("SELECT MIN(IC50_max), MAX(IC50_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ?", (selectedDrug, target, ic50_limit))
            ic50_df = pd.DataFrame(cursor.fetchall())
            ic50_min = ic50_df[0][0]
            ic50_max = ic50_df[1][0]
            
            if ic50_min != None: 
                min_values.append(float(ic50_min))

            if ic50_max != None: 
                max_values.append(float(ic50_max))                

        if min_values and max_values: 
            min_value = min(min_values)
            max_value = max(max_values)

            #con.close()

            return min_value, max_value
        
        else: 
            return None, None

    finally:
        lock.release()


def targetProfileBA(id_list, kd_limit = None, ki_limit = None, ic50_limit = None, Temp = None, pH = None):
    """Retrieve target profiles for a list of drugs with measured binding affinities below set limits and write them to a drug panel file. 
    :param id_list: selected drugs, kd_limit: selected kd threshold, ki_limit: selected ki threshold, ic50_limit: selected ic50 threshold, 
    temp: temperature selected for experimental conditions, ph: pH selected for experimental conditions
    :return: text representing each drugs target profile, text for drug panel file"""

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
    """Retrieve targets for a drug depending on binding affinity values measured below the set thresholds.
    :param drugID: selected drug, kd_limit: selected kd threshold, ki_limit: selected ki threshold, ic50_limit: selected ic50 threshold, 
    temp: temperature selected for experimental conditions, ph: pH selected for experimental conditions
    :return: list if targets identified for the selected drug"""
    
    try:

        #create_connection('DrugTargetInteractionDB.db')
        
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

        #con.close()
        return targetList
    
    finally:
        lock.release()

def transform_value(value):
    """Transform a value to get a logarithmic scale
    :param value: value to be transformed
    :return: value raised to the power of ten with two decimals"""
    
    if value == 0:
        return 0
    else: 
        return round(10 ** value, 2)

@app.callback(Output('cytoscape-tapNodeData-output', 'children'),
              Input('selectedDrugs-output', 'value'),
              Input('cytoscape-drugTargetNet', 'tapNodeData'),
              Input(component_id='kd--slider', component_property='value'), #multiple inputs must also be inside a list
              Input(component_id='ki--slider', component_property='value'),
              Input(component_id='ic50--slider', component_property='value'),
              Input(component_id='temp-input', component_property='value'),
              Input(component_id='ph-input', component_property='value'),

              prevent_initial_call=True
              )

def displayTapNodeData(drug, data, kd_limit, ki_limit, ic50_limit, Temp, pH):
    """Define text with binding affinity information when a node is tapped.
    :param drug: tapped drug node, data: data belonging to the tapped node
    :return: text representing binding affinity measurments for the drug target pair. """

    if data:

        target = data['id']

        kd = transform_value(kd_limit)
        ki = transform_value(ki_limit)
        ic50 = transform_value(ic50_limit)

        minValue, maxValue = minMaxValues(drug, target, kd, ki, ic50, Temp, pH)

        if not minValue and not maxValue:
            return f'Click on a target node for binding affinity information.'

        elif minValue != maxValue:

            sem_value = calculateSem(drug, data, kd, ki, ic50, Temp, pH)

            return f'Binding affinity measured between {drug} and {target}: {minValue} nM to {maxValue} nM. Standard error of the mean is calculated to {sem_value}'

        else:
            return f'Binding affinity measured between {drug} and {target}: {minValue} nM'

def calculateSem(drug, data, kd, ki, ic50, temp, pH):
    
    try:

        #create_connection('DrugTargetInteractionDB.db')
        
        lock.acquire(True)

        target = data['id']

        values = []

        a = 0
        
        if temp != None and pH == None:
            cursor.execute("SELECT Kd_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ? and Temperature = ?", (drug, target, kd, temp))
            kd_df = pd.DataFrame(cursor.fetchall(), columns=["Kd_max"])
            values.extend(kd_df['Kd_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ? and Temperature = ?", (drug, target, kd, temp))            
            kdCount_df = pd.DataFrame(cursor.fetchall())
            a += kdCount_df[0][0]

            cursor.execute("SELECT Ki_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and Temperature = ?", (drug, target, ki, temp))
            ki_df = pd.DataFrame(cursor.fetchall(), columns=["Ki_max"])
            values.extend(ki_df['Ki_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and Temperature = ?", (drug, target, ki, temp))            
            kiCount_df = pd.DataFrame(cursor.fetchall())
            a += kiCount_df[0][0]

            cursor.execute("SELECT IC50_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ? and Temperature = ?", (drug, target, ic50, temp))
            ic50_df = pd.DataFrame(cursor.fetchall(), columns=["IC50_max"])
            values.extend(ic50_df['IC50_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ? and Temperature = ?", (drug, target, ic50, temp))            
            ic50Count_df = pd.DataFrame(cursor.fetchall())
            a += ic50Count_df[0][0]

        elif temp == None and pH != None:
            cursor.execute("SELECT Kd_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ? and pH = ?", (drug, target, kd, pH))
            kd_df = pd.DataFrame(cursor.fetchall(), columns=["K_max"])
            values.extend(kd_df['Kd_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ? and pH = ?", (drug, target, kd, pH))            
            kdCount_df = pd.DataFrame(cursor.fetchall())
            a += kdCount_df[0][0]

            cursor.execute("SELECT Ki_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and pH = ?", (drug, target, ki, pH))
            ki_df = pd.DataFrame(cursor.fetchall(), columns=["Ki_max"])
            values.extend(ki_df['Ki_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and pH = ?", (drug, target, ki, pH))            
            kiCount_df = pd.DataFrame(cursor.fetchall())
            a += kiCount_df[0][0]

            cursor.execute("SELECT IC50_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ? and pH = ?", (drug, target, ic50, pH))
            ic50_df = pd.DataFrame(cursor.fetchall(), columns=["IC50_max"])
            values.extend(ic50_df['IC50_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ? and pH = ?", (drug, target, ic50, pH))            
            ic50Count_df = pd.DataFrame(cursor.fetchall())
            a += ic50Count_df[0][0] 

        elif temp != None and pH != None:

            cursor.execute("SELECT Kd_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ? and Temperature = ? and pH = ?", (drug, target, kd, temp, pH))
            kd_df = pd.DataFrame(cursor.fetchall(), columns=["Kd_max"])
            values.extend(kd_df['Kd_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ? and Temperature = ? and pH = ?", (drug, target, kd, temp, pH))            
            kdCount_df = pd.DataFrame(cursor.fetchall())
            a += kdCount_df[0][0]

            cursor.execute("SELECT Ki_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and Temperature = ? and pH = ?", (drug, target, ki, temp, pH))
            ki_df = pd.DataFrame(cursor.fetchall(), columns=["Ki_max"])
            values.extend(ki_df['Ki_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ? and Temperature = ? and pH = ?", (drug, target, ki, temp, pH))            
            kiCount_df = pd.DataFrame(cursor.fetchall())
            a += kiCount_df[0][0]

            cursor.execute("SELECT IC50_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ? and Temperature = ? and pH = ?", (drug, target, ic50, temp, pH))
            ic50_df = pd.DataFrame(cursor.fetchall(), columns=["IC50_max"])
            values.extend(ic50_df['IC50_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ? and Temperature = ? and pH = ?", (drug, target, ic50, temp, pH))            
            ic50Count_df = pd.DataFrame(cursor.fetchall())
            a += ic50Count_df[0][0]
        
        else: 

            cursor.execute("SELECT Kd_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ?", (drug, target, kd))
            kd_df = pd.DataFrame(cursor.fetchall(), columns=["Kd_max"])
            values.extend(kd_df['Kd_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Kd_max <= ?", (drug, target, kd))            
            kdCount_df = pd.DataFrame(cursor.fetchall())
            a += kdCount_df[0][0]

            cursor.execute("SELECT Ki_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ?", (drug, target, ki))
            ki_df = pd.DataFrame(cursor.fetchall(), columns=["Ki_max"])
            values.extend(ki_df['Ki_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and Ki_max <= ?", (drug, target, ki))            
            kiCount_df = pd.DataFrame(cursor.fetchall())
            a += kiCount_df[0][0]

            cursor.execute("SELECT IC50_max FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ?", (drug, target, ic50))
            ic50_df = pd.DataFrame(cursor.fetchall(), columns=["IC50_max"])
            values.extend(ic50_df['IC50_max'].tolist())
            cursor.execute("SELECT COUNT(*) AS n FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and HGNC = ? and IC50_max <= ?", (drug, target, ic50))            
            ic50Count_df = pd.DataFrame(cursor.fetchall())
            a += ic50Count_df[0][0]

        value = sem(values)
                   
        #con.close()

        return value

    finally:
        lock.release()

        

@app.callback(
    Output("download-text", "data"),
    Output("btn_drugpanel", "n_clicks"),
    Input("btn_drugpanel", "n_clicks"),
    Input('intermediate-text', 'data'),
    Input('filename-input', 'value'),
    prevent_initial_call=True,
)

def func(n_clicks, intText, name):
    """Downlowd drug panel file when  the download-drug-panel button is pressed
    :param n-clicks: number of times the button is clicked, intText: text to be represented in the drug panel file, name: filename
    :return: textfile representing the drugpanel"""

    if n_clicks is None:
        raise PreventUpdate
    else:
        n_clicks = None
        return dict(content=intText, filename=name), n_clicks

if __name__ == '__main__':
    app.run_server(debug=True)


con.close()


