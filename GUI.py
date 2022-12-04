from dash import Dash, html, dcc, Input, Output, exceptions, no_update
import plotly.express as px

import pandas as pd
import sqlite3

# https://towardsdatascience.com/dashing-through-christmas-songs-using-dash-and-sql-34ef2eb4d0cb



app = Dash(__name__)

colors = {
    'background': '#ECF9FF',
    'text': '#000000'
}



df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

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
        html.Label('Drug IDs'),
        html.Br(),
        dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'],
                     'Montréal',
                     multi=True, # If true, the user can select multiple values
                     #value = [],
                     id='drugID-dropdown'), #list er ikke riktig
     ], style={'margin-bottom': -150, 'padding': 100, 'flex': 1, 'height':10, 'width':1000}),

    html.Div([
        html.H3("Binding Affinity Thresholds"),
        html.Label('Kd slider'),
        dcc.Slider(
            min=0,
            max=10,
            step=1,
            value=0,
            marks={i: f'{i}' if i == 1 else str(i) for i in range(0, 10)},
            id='kd--slider'
        ),

        html.Br(),
        html.Label('Ki slider'),
        dcc.Slider(
            min=0,
            max=10,
            step=1,
            value=0,
            marks={i: f'{i}' if i == 1 else str(i) for i in range(0, 10)},
            id='ki--slider'
        ),

        html.Br(),
        html.Label('IC50 slider'),
        dcc.Slider(
            min=0,
            max=10,
            step=1,
            value=0,
            marks={i: f'{i}' if i == 1 else str(i) for i in range(0, 10)},
            id='ic50--slider'
        ),

        html.H3('Experimental conditions'),

        'Temperature: ',
        dcc.Input(id='temp-input', value='initial value', type='text'),

        html.Br(),
        html.Br(),
        "pH: ",
        dcc.Input(id='ph-input', value='initial value', type='text'),

        dcc.Graph(id='graph_output', figure = {}) #figure is a dict for the graph component
        ], style={'margin-top': '0','padding': 100, 'height':15, 'width':300, 'color': colors['text']}), # H Head line (number indicates size (1-6))),


    html.Div(children =[
        html.Button("Download drug panel", id="btn_drugpanel"), 
        dcc.Download(id="download-text-index")
        ], style={'padding-left': '70%', 'margin-top': -92})

])

#Every callback needs at least one oínput and one output
#Every single pair of output can only have one callback
@app.callback(
    [Output(component_id='drugID-dropdown', component_property='children'), #Multiple outputs muse be placed inside a list
    Output(component_id='graph_output', component_property='children')], # Output is the children property of the component with the ID 'graph-with-slicer'
    [Input(component_id='drugID-dropdown', component_property='value'), 
    Input(component_id=('kd--slider'), component_property='value'), #multiple inputs must also be inside a list
    Input(component_id='ki--slider', component_property='value'),
    Input(component_id='ic50--slider', component_property='value')] #need to return as many figures as you have inputs
    , #State can be used if a button should be clicked to update a figure (might be used for pH, temp and to download drugpanel)
    #, prevent_initial-call=True #Doesn't trigger all call back when the page is refreshed.
    )
def update_figure(drugID_list, kd_value, ki_value, ic50_value): # Input referes to component property of input, same as saying that the input is the value declared in app.layout. 
    if len(drugID_list) == 0:
        return no_update, no_update
    
    if len(drugID_list) > 0: 
        print(f'value user chose: {drugID_list}')
        print(type(drugID_list))
        #remember to make a copy of the df if yo change it
        dict = {'kd':kd_value, 'ki':ki_value, 'ic50':ic50_value}
        print(dict)
        dff = pd.DataFrame.from_dict(dict, orient='index')
        print(dff)
        fig = px.pie(dff, title='Binding Affinity Values')
        #fig.update_traces(textinfo='value+precent').update_layout(title_x=0.5)
    
    #Can be used to prevent update if no values are chosen
    """
    elif len(val_chosen) == 0: 
        raise exceptions.PreventUpdate 
    """
    return no_update, fig 

if __name__ == '__main__':
    app.run_server(debug=True)