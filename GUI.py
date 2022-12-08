from dash import Dash, html, dcc, Input, Output, exceptions, no_update
import plotly.express as px
import dash_cytoscape as cyto

import pandas as pd
import sqlite3
import threading
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
    }
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
        #html.Div(id='drugPanel-output', style = {'margin-left': -50, 'margin-top': -80, 'width':600})
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
        html.P(id='cytoscape-mouseoverNodeData-output'),
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
    Output(component_id='cytoscape-drugTargetNet', component_property='elements')
    ], #Multiple outputs muse be placed inside a list, Output is the children property of the component with the ID 'graph-with-slicer'
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
        return 'Threshold selected for Kd: {}'.format(kd), 'Threshold selected for Ki: {}'.format(ki), u'Threshold selected for IC\u2085\u2080: {}'.format(ic50), no_update, no_update, no_update
    
    elif len(drugID_list) > 0 and selectedDrug == None:
        dp = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        netOptions = radioItemsOptions(drugID_list)
        return 'Threshold selected for Kd: {}'.format(kd), 'Threshold selected for Ki: {}'.format(ki), u'Threshold selected for IC\u2085\u2080: {}'.format(ic50), netOptions, dp, no_update
    else: 
        dp = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        netOptions = radioItemsOptions(drugID_list)
        netElements = drugTargetNet(selectedDrug, kd_limit = kd, ki_limit = ki, ic50_limit = ic50, Temp = temp, pH = ph)
        return 'Threshold selected for Kd: {}'.format(kd), 'Threshold selected for Ki: {}'.format(ki), u'Threshold selected for IC\u2085\u2080: {}'.format(ic50), netOptions, dp, netElements

def radioItemsOptions(drugID_list):
    options = [{'label': x, 'value': x} for x in drugID_list]
    return options

def drugTargetNet(selectedDrug, kd_limit = None, ki_limit = None, ic50_limit = None, Temp = None, pH = None):
    try: 

        # Network for selected drug where node size depends on binding affinity
        targets = sorted(targetList(selectedDrug, kd_limit, ki_limit, ic50_limit, pH, Temp))
        #elements = [{'data': {'id': 'drug', 'label': selectedDrug}, 'position': {'x': 50, 'y': 50}, 'size':50}]
        elements = [{'data': {'id': 'drug', 'label': selectedDrug}, 'position': {'x': 50, 'y': 50}}]
        a = 200
        b = 200

        create_connection('DrugTargetInteractionDB.db')

        lock.acquire(True)

        for i in targets:
            #elements.append({'data': {'id': i, 'label': i}, 'position': {'x': 200, 'y': 200}, 'size':70}) 
            #elements.append({'data': {'source': 'drug', 'target': i,'label': f'Node {selectedDrug} to {i}'}})

            min_values = []

            cursor.execute("SELECT MIN(Kd_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  HGNC = ?", (selectedDrug, i))
            kd_pd = pd.DataFrame(cursor.fetchall())
            kd_min = kd_pd[0][0]
            if kd_min != None: 
                min_values.append(float(kd_min))

            cursor.execute("SELECT MIN(Ki_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  HGNC = ?", (selectedDrug, i))
            ki_pd = pd.DataFrame(cursor.fetchall())
            ki_min = ki_pd[0][0]
            if ki_min != None:
                min_values.append(float(ki_min))

            cursor.execute("SELECT MIN(IC50_max) FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  HGNC = ?", (selectedDrug, i))
            ic50_pd = pd.DataFrame(cursor.fetchall())
            ic50_min = ic50_pd[0][0]
            if ic50_min != None: 
                min_values.append(float(ic50_min))

            min_value = min(min_values)
            
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
            
            elements.append(targetDict) 

            edgeData = {}
            edgeData['source'] = 'drug'
            edgeData['target'] = i
            edgeData['label'] = f'Node {selectedDrug} to {i}'

            edgeDict = {}
            edgeDict['data'] = edgeData

            elements.append(edgeDict)
        
        con.close()
        
        return elements
    
    finally:
        lock.release()


def targetProfileBA(id_list, kd_limit = None, ki_limit = None, ic50_limit = None, Temp = None, pH = None):
    """Retrieve target profiles for a list of drugs with measured binding affinities below set limits and write them to a drug panel file. 
    :param db_file: database db_file, file_name: name for drugpanel file, id_list: list of drug IDs, kd_limit: Upper limit for kd value for binding affinity, ki_limit: Upper limit for ki value for binding affinity, ic50_limit: Upper limit for ic50 value for binding affinity. 
    """

    complete_dp = []
    for i in id_list:
        
        targets = targetList(i, kd_limit, ki_limit, ic50_limit, pH, Temp)
    
        if len(targets) > 0: 
            #dp = i + "\t" + "inhibits" + "\t" + ",\t".join(sorted(set(targets))) #+ "\n" # comma must be removed if this should be used to make the drugtarget panel
            dp = f'{i} inhibits {", ".join(sorted(set(targets)))}'
            complete_dp.append(dp)
            complete_dp.append(html.Br())

        targets.clear()
    
    return complete_dp

def targetList(drugID, kd_limit, ki_limit, ic50_limit, pH, temp):
    try:

        create_connection('DrugTargetInteractionDB.db')
        
        lock.acquire(True)
        
        frames = []

        if temp != None and pH == None:
            if kd_limit != None:
                cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  Kd_max <= ? and Temperature = ?", (drugID, kd_limit, temp))
                df1 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
                frames.append(df1)

            if ki_limit != None: 
                cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  Ki_max <= ? and Temperature = ?", (drugID, ki_limit, temp))
                df2 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
                frames.append(df2)

            if ic50_limit: 
                cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  IC50_max <= ? and Temperature = ?", (drugID, ic50_limit, temp))
                df3 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
                frames.append(df3)
        
        elif pH != None and temp == None: 
            if kd_limit != None:
                cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  Kd_max <= ? and pH = ?", (drugID, kd_limit, pH))
                df1 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
                frames.append(df1)

            if ki_limit != None: 
                cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  Ki_max <= ? and pH = ?", (drugID, ki_limit, pH))
                df2 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
                frames.append(df2)

            if ic50_limit: 
                cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  IC50_max <= ? and pH = ?", (drugID, ic50_limit, pH))
                df3 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
                frames.append(df3)
        
        elif pH != None and temp != None: 
            if kd_limit != None:
                cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  Kd_max <= ? and Temperature = ? and pH = ?", (drugID, kd_limit, temp, pH))
                df1 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
                frames.append(df1)

            if ki_limit != None: 
                cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  Ki_max <= ? and Temperature = ? and pH = ?", (drugID, ki_limit, temp, pH))
                df2 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
                frames.append(df2)

            if ic50_limit: 
                cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  IC50_max <= ? and Temperature = ? and pH = ?", (drugID, ic50_limit, temp, pH))
                df3 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
                frames.append(df3)
        
        else: 
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
    
    finally:
        lock.release()

def transform_value(value):
    if value == 0:
        return 0
    else: 
        return round(10 ** value, 2)

@app.callback(Output('cytoscape-tapNodeData-output', 'children'),
              Input('cytoscape-drugTargetNet', 'tapNodeData'))

def displayTapNodeData(data):
    if data:
        return f'Binding affinity between the drug-target pair: {data["size"]/100} nM' 

'''@app.callback(
    Output('intermediate-text', 'data'),
    [Input(component_id='drugID-dropdown', component_property='value'), 
    Input(component_id='kd--slider', component_property='value'), #multiple inputs must also be inside a list
    Input(component_id='ki--slider', component_property='value'),
    Input(component_id='ic50--slider', component_property='value'),
    Input(component_id='temp-input', component_property='value'),
    Input(component_id='ph-input', component_property='value')
    ],
    prevent_initial_call=True
)


def targetProfileDownload(id_list, kd_limit = None, ki_limit = None, ic50_limit = None, Temp = None, pH = None):
    """Retrieve target profiles for a list of drugs with measured binding affinities below set limits and write them to a drug panel file. 
    :param db_file: database db_file, file_name: name for drugpanel file, id_list: list of drug IDs, kd_limit: Upper limit for kd value for binding affinity, ki_limit: Upper limit for ki value for binding affinity, ic50_limit: Upper limit for ic50 value for binding affinity. 
    """
    
    if  str(type(id_list)) != "<class 'NoneType'>":

        print("id_list: ", id_list)

        text = "#Name\tTarget:\n"
        
        for i in id_list:
            targets = targetList(i, kd_limit, ki_limit, ic50_limit, pH, Temp)

            print(targets)

            if len(targets) > 0:
                text = text + i + '\tinhibits\t' + '\t'.join(sorted(set(targets))) + '\n'
        
        print(type(text))
        print(type(file_name))

        print("Text: ")
        print(text)
        
        return text
    
    else:
        return no_update


@app.callback(
    Output('download-text', 'data'),
    Input('btn_drugpanel', 'n_clicks'),
    Input('intermediate-text', 'data'),
    Input(component_id='filename-input', component_property='value'),
    prevent_initial_call=True
)

def func(n_clicks, text, fileName):

    print(text)

    return dict(content=text, filename=fileName)'''

'''@app.callback(
    Output("download-text", "data"),
    Input("btn_drugpanel", "n_clicks"),
    prevent_initial_call=True,
)

def func(n_clicks):
    return dict(content="Hello world!", filename="hello.txt")'''

if __name__ == '__main__':
    app.run_server(debug=True)