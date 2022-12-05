from dash import Dash, html, dcc, Input, Output, exceptions, no_update
import plotly.express as px

import pandas as pd
import sqlite3
from aifc import Error

# https://towardsdatascience.com/dashing-through-christmas-songs-using-dash-and-sql-34ef2eb4d0cb

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
    'background': '#ECF9FF',
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
     ], style={'margin-bottom': -150, 'padding': 100, 'width':1330, 'backgroundColor': colors['background']}),

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

        html.Div(id='ic50-output-container', style={'margin-top': 20}),

        html.H3('Experimental conditions'),

        'Temperature: ',
        dcc.Input(id='temp-input', value='initial value', type='text'),

        html.Br(),
        html.Br(),
        "pH: ",
        dcc.Input(id='ph-input', value='initial value', type='text')
        ], style={'margin-top': '0','padding': 100, 'height':15, 'width':600, 'color': colors['text']}), # H Head line (number indicates size (1-6))),


    html.Div([
        html.Button("Download drug panel", id="btn_drugpanel"), 
        dcc.Download(id="download-text-index")
        ], style={'padding-left': '70%', 'margin-top': -92}),

    html.Br(),
    html.Div(id='drugPanel-output', style = {'padding-left': '50%', 'padding-right':'23%','margin-top': -10, 'text-align': 'right'})


])

#Every callback needs at least one oínput and one output
#Every single pair of output can only have one callback
@app.callback(
    [#Output(component_id='drugID-dropdown', component_property='children'),
    Output(component_id='kd-output-container', component_property='children'),
    Output(component_id='ki-output-container', component_property='children'),
    Output(component_id='ic50-output-container', component_property='children'),
    Output(component_id='drugPanel-output', component_property='children')], #Multiple outputs muse be placed inside a list, Output is the children property of the component with the ID 'graph-with-slicer'
    [Input(component_id='drugID-dropdown', component_property='value'), 
    Input(component_id='kd--slider', component_property='value'), #multiple inputs must also be inside a list
    Input(component_id='ki--slider', component_property='value'),
    Input(component_id='ic50--slider', component_property='value')] #need to return as many figures as you have inputs
     #State can be used if a button should be clicked to update a figure (might be used for pH, temp and to download drugpanel)
    #, prevent_initial-call=True #Doesn't trigger all call back when the page is refreshed.
    )

def update_figure(drugID_list, kd_value, ki_value, ic50_value): # Input referes to component property of input, same as saying that the input is the value declared in app.layout. 
    
    kd = transform_value(kd_value)
    ki = transform_value(ki_value)
    ic50 = transform_value(ic50_value)
    print(kd, ki, ic50)
    
    if len(drugID_list) == 0:
        return 'Threshold selected for Kd: "{}"'.format(kd), 'Threshold selected for Ki: "{}"'.format(ki), u'Threshold selected for IC\u2085\u2080: "{}"'.format(ic50), no_update,
    
    else: 
        print(f'value user chose: {drugID_list}')
        #remember to make a copy of the df if you change it
        dp = targetProfileBA(drugID_list, kd_limit = kd, ki_limit = ki, ic50_limit = ic50)

        return 'Threshold selected for Kd: "{}"'.format(kd), 'Threshold selected for Ki: "{}"'.format(ki), u'Threshold selected for IC\u2085\u2080: "{}"'.format(ic50), dp

def targetProfileBA(id_list, kd_limit = None, ki_limit = None, ic50_limit = None):
    """Retrieve target profiles for a list of drugs with measured binding affinities below set limits and write them to a drug panel file. 
    :param db_file: database db_file, file_name: name for drugpanel file, id_list: list of drug IDs, kd_limit: Upper limit for kd value for binding affinity, ki_limit: Upper limit for ki value for binding affinity, ic50_limit: Upper limit for ic50 value for binding affinity. 
    """
    create_connection('DrugTargetInteractionDB.db')

    complete_dp = ""
    for i in id_list:
        frames = []
        if kd_limit != None:
            cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  Kd_max <= ?", (i, kd_limit))
            df1 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
            frames.append(df1)

        if ki_limit != None: 
            cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  Ki_max <= ?", (i, ki_limit))
            df2 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
            frames.append(df2)

        if ic50_limit: 
            cursor.execute("SELECT DISTINCT drugID, HGNC FROM MeasuredFor INNER JOIN BindingAffinity ON MeasuredFor.BindingReactionID = BindingAffinity.BindingReactionID WHERE DrugID = ? and  IC50_max <= ?", (i, ic50_limit))
            df3 = pd.DataFrame(cursor.fetchall(), columns=["drugID", "HGNC"])
            frames.append(df3)
            
        dp_df = pd.concat(frames, ignore_index=True)

        targetList = []
        for ind in dp_df.index:
            drugId = dp_df["drugID"][ind]
            aT = "Inhibits"
            targetList.append(dp_df["HGNC"][ind])
    
        if len(targetList) > 0: 
            dp = drugId + "\t" + aT + "\t" + ",\t".join(sorted(set(targetList))) #+ "\n" # comma must be removed if this should be used to make the drugtarget panel
            complete_dp = complete_dp + "\n" + dp

        frames.clear()
   
    print(complete_dp)
    con.close()
    
    return complete_dp

def transform_value(value):
    if value == 0:
        return 0
    else: 
        return round(10 ** value, 2)


if __name__ == '__main__':
    app.run_server(debug=True)