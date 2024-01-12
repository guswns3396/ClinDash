import base64
import io

from dash import Dash, dcc, html, Input, Output, State, callback, dash_table
from dash.exceptions import PreventUpdate

import plotly.express as px

import pandas as pd

app = Dash(__name__)

DATA = {}

app.layout = html.Div([
    dcc.Upload(
        id='data-upload',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True,
        # only accept csvs
        accept='.csv'
    ),
    html.P('Files'),
    html.Div(
        id='data-dropdown-div',
        children=dcc.Dropdown(list(DATA.keys()), id='data-dropdown')
    ),
    html.Div(
        id='data-table'
    ),
    dcc.Graph(id='data-pie')
])


def read_data(contents, filename):
    '''
    parse the contents & filename of upload
    :param contents:
    :param filename:
    :return: return df or e
    '''
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            return df
    except Exception as e:
        return e


@callback(Output('data-dropdown-div', 'children'),
          Input('data-upload', 'contents'),
          State('data-upload', 'filename'))
def update_after_upload(list_of_contents, list_of_names):
    '''
    upon upload
    get 'contents' and 'filename' attributes from 'data-upload' element as input
    parse the uploaded files
    store data
    output to "output-data-upload" element under "children" attribute as dropdown
    :param list_of_contents:
    :param list_of_names:
    :return: dropdown
    '''
    if list_of_contents is not None:
        # store data
        DATA.update({
            filename: read_data(contents, filename)
            for contents, filename in zip(list_of_contents, list_of_names)
        })
    # output as dropdown
    children = dcc.Dropdown(list(DATA.keys()), id='data-dropdown')
    return children


@callback(
    [Output('data-table', 'children'), Output('data-pie', 'figure')],
    Input('data-dropdown', 'value')
)
def update_after_dropdown(value):
    '''
    output table when dropdown selected
    :param value: dropdown value
    :return: table
    '''
    if value is not None:
        # parse data
        parsed = parse_data(value)
        # render parsed data
        return dash_table.DataTable(data=parsed['table'], page_size=10), parsed['pie']
    raise PreventUpdate


def parse_data(value):
    '''
    function to actually parse data into desired format
    :param value: name of file
    :return:
    '''
    parsed = {}
    df = DATA[value]
    parsed['table'] = df.to_dict('records')
    parsed['pie'] = px.pie(df, values=' duration', names=' description', hole=.3)
    return parsed


if __name__ == '__main__':
    app.run(debug=True)
