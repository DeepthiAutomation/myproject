import pandas as pd
import numpy as np
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input,Output
from dash import callback_context
import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

load_figure_template('LUX')


###--------------Build the figures / dropdowns------------------------------------

x = np.random.sample(100)
y = np.random.sample(100)
z = np.random.choice(a = ['a','b','c'], size = 100)


df1 = pd.DataFrame({'x': x, 'y':y, 'z':z}, index = range(100))

fig1 = px.scatter(df1, x= x, y = y, color = z)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#008b8b",
    'text': 'white'
}
#app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(
                name=__name__,
               external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True
                )
ALLOWED_TYPES = (
    "text", "password", "email"
)

sidebar = html.Div(
    [ html.Img(src=app.get_asset_url('logo.png'), width=50, height=50,style = {'margin-left':'30px','margin-top':'7px'}),

        dbc.Nav(
            [
                html.Div(dcc.Input(id='input-on-submit', type='text')),html.Button('Submit', id='submit-val', n_clicks=0),
    html.Div(id='container-button-basic',
             children='Enter a value and press submit')]
        ),
    ],
    style=SIDEBAR_STYLE,
)


###---------------Create the layout of the app ------------------------

ALLOWED_TYPES = (
    "text",  "password", "email", 
)

app.layout = html.Div(children = [dbc.Row([dbc.Col(sidebar)]),
                dbc.Row([
                    dbc.Col(),

                    dbc.Col(html.H1('Welcome to Acess management automation Portal',className="lead"),width = 9, style = {'margin-left':'50px','margin-top':'5px'})
                    ]),
                    dbc.Row(    [    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '30%',
            'height': '40px',
            'lineHeight': '40px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'margin-left':'400px',
            'background': 'white',
            'text': 'black'
        },
        # Allow multiple files to be uploaded
        multiple=True
    )]),
                dbc.Row(
                    [dbc.Col(html.Div(id='output-data-upload'),width = 9, style = {'margin-left':'300px', 'margin-top':'7px', 'margin-right':'15px'}),
                    #dbc.Col(dcc.Graph(id = 'graph1', figure = fig1), width = 9, style = {'margin-left':'35px', 'margin-top':'7px', 'margin-right':'15px'})
                    html.Div(id='datatable-interactivity-container'),
                    
                    ]),],
 
)
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
    },
    fill_width=True,
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
    ), 
        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff =  pd.DataFrame(rows)
    #print(dff.iloc[0])
    print(derived_virtual_selected_rows)
    for i in derived_virtual_selected_rows:
        print(dff.iloc[i])

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        #dff["country"]
    ]
@app.callback(
    Output('container-button-basic', 'children'),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', 'derived_virtual_selected_rows'),
    
)
def update_output(rows, selectedrows):
    df2=pd.DataFrame(rows)
    k=[]
    print("selected rows are {}".format(selectedrows))
    print(df2.iloc[selectedrows])
    df3=df2.iloc[selectedrows]
    L=df3.values.tolist()
    print("list is {}".format(L))

    return 'The input value was "{}" '.format(
        L
    )

if __name__ == '__main__':
    app.run_server(port = 9001, debug=True)