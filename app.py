'''
This is all about making a pretty output that is interactive

Create dashboard app to receive notifications for ADTs:
 - automatically refreshes
- display as a table
- filter by time, type and topic
Use reciever as Flask app with Post to get notifications
Save notifications in a CSV file to start then as a database
Consider saving as native json
Deploy to Pythonanywhere

future stuff
 - add about me link
 - click on notification and get bundle back Using flask app (using transaction or a series of gets) and display as a card next to the table
as a narrative of the results
    - limit active cells only to event_id rows
    - create and use hidden row data and display only clickable id columns
    - link to actual id data
    - put cards next each other
    - links to to resouces
    - audit logging
'''

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input, State
import dash_table
import get_resources as get_res

my_path='/Users/ehaas/Documents/Python/Flask-pubsub-endpoint/' #local build
#my_path='Flask-pubsub-endpoint/' #pythonanywhere build

my_topics = {
        "All-Topics":"all",
        'Encounter-Start': 'http://argonautproject.org/encounters-ig/SubscriptionTopic/encounter-start',
        'Encounter-End': 'http://argonautproject.org/encounters-ig/SubscriptionTopic/encounter-end',
        'Encounter-Transfer': 'http://argonautproject.org/encounters-ig/SubscriptionTopic/encounter-transfer',
         }

my_types = [
        "all-types",
        'handshake',
        'heartbeat',
        'event-notification',
        'query-status',
        ]

data_columns = [
        'timestamp',
        'type',
        'status',
        'topic',
        'event_id',
        ]

# data = pd.read_csv("/Users/ehaas/Documents/Python/Flask-pubsub-endpoint/data.csv")
# data["timestamp"] = pd.to_datetime(data["timestamp"], format="%Y-%m-%d")
# data.sort_values("Date", inplace=True)
# #new_data = data[['Date','AveragePrice']].head()


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Da Vinci ADT Notifier!"

app.layout = html.Div(
    children=[
        dcc.Interval(
            id='interval-component',
            interval=15*1000, # in milliseconds (every 15 seconds)
            n_intervals=0
        ),
        html.Div(
            children=[
            html.Div([
                html.Img(
                        src = app.get_asset_url('fhir-logo-www.png'),
                        height = '43 px',
                        width = 'auto',
                        style = {'float': 'left',},
                        ),
                html.Img(
                        src = app.get_asset_url('da-vinci_logo.jpeg'),
                        height = '43 px',
                        width = 'auto',
                        style = {'float': 'right',},
                    ),
                html.H1(
                    children="ADT Notifier",
                    className="header-title",
                    #style={"display": "inline", "float":"center,"},
                )
                ],
                style = {
                        'align-items': 'center',
                        'padding-top' : '1%',
                        'padding-left' : '1%',
                        'padding-right' : '1%',
                        'height' : 'auto',}
                    ),

                html.P(
                    children="Da Vinci Notifications project is planning to adopt the updated FHIR Subscriptions framework for its use cases.  This Dashboard demonstrates using subscriptions to notify a careteam member of ADT events.",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Topic", className="menu-title"),
                        dcc.Dropdown(
                            id="topic-filter",
                            options=[
                            {"label": k, "value": v, "title": v}
                             for k,v in my_topics.items()
                            ],
                            value="all",
                            clearable=False,
                            className="dropdown"
                        )
                    ],
                    style={"width": "25%"}
                ),
                html.Div(
                    children=[
                        html.Div(children="Type", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[
                                {"label": my_type, "value": my_type,}
                                for my_type in my_types
                            ],
                            value="all-types",
                            clearable=False,
                            searchable=False,
                            className="dropdown"
                        )
                    ],
                    style={"width": "25%"}
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange( # todo update dynamically
                            id="date-range",
                            clearable=True,
                        )
                    ]
                )
            ],
            className="menu"
        ),
        html.Div(
            children=[

                html.Div(
                    children=dash_table.DataTable(
                        id="noti-table",
                        columns = [ {'name' : i , 'id': i} for i in data_columns],
                    style_cell={'textAlign': 'left'},
                    # style_cell_conditional=[
                    #     {
                    #         'if': {'column_id': 'topic'},
                    #         'textAlign': 'left'
                    #     },],
                    style_header={
                        'backgroundColor': 'rgb(500, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    #style_as_list_view=True,

                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Markdown(
                        id = "click-data",
                        style={
                            'backgroundColor': 'rgb(255, 255, 255)',
                        },
                        ),
                    className="card",
                ),
            ],
            className="wrapper"
        )
    ]
)

# define callback
@app.callback(
    Output('click-data', 'children'),
    [Input('noti-table', 'active_cell')],
     # (A) pass table as data input to get current value from active cell "coordinates"
    [State('noti-table', 'data')]
)
def display_click_data(active_cell, table_data):
    if active_cell:
        #cell = dumps(active_cell, indent=2)
        row = active_cell['row']
        col = active_cell['column_id']
        value = table_data[row][col]
        out = get_res.enc_data(
                my_type="Encounter",
                my_id="2081026",
                my_base="http://hapi.fhir.org/baseR4",
                )  # use value to get data through a series of Gets and return as a table of data
        out = f'### Encounter {value} Data\n\n{out}'
    else:
        value = "no value"
        out = 'no cell selected'

    #return f'{value} gets you: {dumps(out, indent=2)}'
    return out

@app.callback(
    [
        Output("date-range", "min_date_allowed"),
        Output("date-range", "max_date_allowed"),
        Output("date-range", "start_date"),
        Output("date-range", "end_date"),
    ],

    [
        Input('interval-component', 'n_intervals'),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_period(n_intervals, start_date, end_date):
    data = pd.read_csv(f"{my_path}data.csv")
    data["timestamp"] = pd.to_datetime(data["timestamp"], format="%Y-%m-%d")
    #print(f'data.timestamp.min().date()= {data.timestamp.min().date()}')
    min_da=data.timestamp.min().date()
    max_da=data.timestamp.max().date()
    my_start_date=data.timestamp.min().date() if start_date is None else start_date
    my_end_date=data.timestamp.max().date() if end_date is None else end_date

    return [min_da,max_da,my_start_date,my_end_date]

@app.callback(
    [
        #Output("price-chart", "figure"),
        Output("noti-table", "data"),
    ],
    [
        Input("topic-filter", "value"),
        Input("type-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input('interval-component', 'n_intervals'),
    ],
)
def update_charts(topic, my_type, start_date, end_date, n_intervals):
    data = pd.read_csv(f"{my_path}data.csv")

    data["timestamp"] = pd.to_datetime(data["timestamp"], format="%Y-%m-%d")
    print(data['timestamp'])
    mask = (
         (data.timestamp.dt.strftime('%Y-%m-%d') >= start_date)
      & (data.timestamp.dt.strftime('%Y-%m-%d') <= end_date)
        )
    data = data.loc[mask, :]

    if  topic != 'all':
        data = data.loc[data["topic"]==topic]
    if  my_type != 'all-types':
        data = data.loc[data["type"]==my_type]

    sorted_filtered_data = data.sort_values("timestamp", ascending=False)
    volume_chart_data = sorted_filtered_data.to_dict('records')

    return (
        volume_chart_data,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
