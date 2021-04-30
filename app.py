'''
Create dashboard app to receive notifications for ADTs
display as a table
sort by time, person, provider, etc - future
Use reciever as Flask app with Post to get notifications
Save notifications in a CSV file to start then as a database
Consider saving as native json
Deploy to Pythonanywhere

This is all about making a pretty output that is interactive

future stuff
 - click on notification and get bundle back Using flask app (using transaction or a series of gets) and display as a card next to the table
 - add an update button (or automatically refresh)
 - generate a narrative of the results
'''



import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
import dash_table

my_types = [
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
app.title = "Using Subscriptions for Da Vinci Notifications!"

app.layout = html.Div(
    children=[
        dcc.Interval(
            id='interval-component',
            interval=5*1000, # in milliseconds (every 5 seconds)
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
                            value="http://argonautproject.org/encounters-ig/SubscriptionTopic/encounter-start",
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
                                {"label": my_type, "value": my_type}
                                for my_type in my_types
                            ], # todo make static list!!
                            value="event-notification",	
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
                        id="volume-chart",
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
                )

            ],
            className="wrapper"
        )
    ]
)

@app.callback(
    Output("topic-filter", "options"),
    [
        Input('interval-component', 'n_intervals'),
    ],
)
def update_topics(n_intervals):
    data = pd.read_csv("/Users/ehaas/Documents/Python/Flask-pubsub-endpoint/data.csv")
    my_options=[{"label": topic, "value": topic} for topic in np.sort(data.topic.unique())]
    #print(my_options)
    return my_options

@app.callback(
    [
        Output("date-range", "min_date_allowed"),
        Output("date-range", "max_date_allowed"),
        Output("date-range", "start_date"),
        Output("date-range", "end_date"),
    ],

    [
        Input('interval-component', 'n_intervals'),
    ],
)
def update_topics(n_intervals):
    data = pd.read_csv("/Users/ehaas/Documents/Python/Flask-pubsub-endpoint/data.csv")
    data["timestamp"] = pd.to_datetime(data["timestamp"], format="%Y-%m-%d")
    #print(f'data.timestamp.min().date()= {data.timestamp.min().date()}')
    min_da=data.timestamp.min().date()
    max_da=data.timestamp.max().date()
    my_start_date=data.timestamp.min().date()
    my_end_date=data.timestamp.max().date()
   
    return [min_da,max_da,my_start_date,my_end_date]  

@app.callback(
    [
        #Output("price-chart", "figure"),
        Output("volume-chart", "data"),
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
    data = pd.read_csv("/Users/ehaas/Documents/Python/Flask-pubsub-endpoint/data.csv")
    #data["timestamp"] = pd.to_datetime(data["timestamp"], format="%Y-%m-%d")
    # mask = (
    #     (data.topic == topic)
    #     & (data.type == my_type)
    #     & (data.timestamp >= start_date)
    #     & (data.timestamp <= end_date)
    # )
    # filtered_data = data.loc[mask, :]
    

    #volume_chart_data = filtered_data.to_dict('records')
    volume_chart_data = data.to_dict('records')
    
    return (
        volume_chart_data,
    )


if __name__ == "__main__":
    app.run_server(debug=True)