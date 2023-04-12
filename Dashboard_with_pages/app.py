from dash import Dash, dcc, html, Input, Output, State, ctx
import dash
import pandas as pd
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import random
from plotly.graph_objs import *
import requests

# The app.py page does not actually contain the pages that are being loaded, it is more so a container
# for pages. It only contains the sidebar (containing buttons to navigate) and a page_container.
# The page container then loads the actual pages from the pages directory.
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)


app.layout = html.Div(children=[ 

    html.Div(id="Sidebar",children=[
        html.Div(children=[
            html.H2("Systematic"),

            # The alert button is only for development purposes.
            dbc.Button("Alert", color="primary",id="AlertBTN"),
        ]),
        html.Div(
        [
            html.Div(
                dbc.Button(f"{page['name']}", color="secondary",class_name="SideBTN",href=page["relative_path"]),
                style={"margin-top" : "5vh","margin-left" : "2%"},
            )
            for page in dash.page_registry.values()
        ]
    ),
    
    ],style={"background-color" : "#e0e0d1","width" : "20vw","height" : "160vh"}),




    html.Div(id="Main-panel",children=[

            dash.page_container

    ]),
    dbc.Alert(
        [
            html.H4("New anomaly detected. \U0001f6d1", className="alert-heading"),
            html.P(
                "Choose to review it now or later."
            ),
            html.Div(
                [dbc.Button(
                    "Not now", id="later", className="ms-auto"
                ),
                dbc.Button(
                    "Go to anomaly", id="close", className="ms-auto", n_clicks=0, href= '/anomalies'
                )]
            ),
        ],
        id="alertMsg",
        is_open=False, #Not sure if this line should be here.
    ),
    dcc.Interval(
                id='interval-component',
                interval=1 * 10000,
                n_intervals=0
            ),
    ], style={"display":"flex","width" : "100vw"})


@app.callback(
    Output("alertMsg", "is_open"),
    Input('interval-component', 'n_intervals'), 
    Input("close", "n_clicks"), 
    Input("later", "n_clicks"),
    State("alertMsg", "is_open"),
)
def toggle_alert(n1, n2, n3, is_open):
    triggered_id = ctx.triggered_id
    if triggered_id == 'interval-component':
        return check_for_new_anomalies(is_open)
    else: return not is_open


def check_for_new_anomalies(is_open):
    anomalies = requests.get("http://localhost:8002/anomalies/getAnomalyList").json()
    print(anomalies)
    #Emy start here
    if is_open:
        return is_open
  #If no new anomaly
    return is_open 


#Debug true allows for hot reloading while writing code.
if __name__ == "__main__":
    app.run(debug=True)