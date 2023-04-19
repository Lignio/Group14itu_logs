from dash import Dash, dcc, html, Input, Output, State, ctx
import dash
import pandas as pd
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
from flask import Flask
from flask_caching import Cache
from plotly.graph_objs import *
from flask_restful import Resource, Api

# The app.py page does not actually contain the pages that are being loaded, it is more so a container
# for pages. It only contains the sidebar (containing buttons to navigate) and a page_container.
# The page container then loads the actual pages from the pages directory.

#Creates server/api
server = Flask(__name__)
api = Api(server)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

#This chache keeps track of new anomalies.
cache = Cache(app.server, config={
    'CACHE_TYPE': 'SimpleCache'
})

cache.set("isFlagged", False)

#Api call that flags an anomily though the cache.
class Flag(Resource):
    def get(self):
        cache.set("isFlagged", True)
        return {cache.get("isFlagged")}
    
api.add_resource(Flag, "/flagNewAnomaly")    

#Layout starts here
app.layout = html.Div(children=[ 

    html.Div(id="Sidebar",children=[
        html.Div(children=[
            html.H2("Systematic"),
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
                    "Dismis", id="dismis", className="ms-auto"
                ),
                dbc.Button(
                    "Go to anomaly", id="goTo", className="ms-auto", n_clicks=0, href= '/anomalies'
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

#@api.post("/flagNewAnomaly")
#def flag():
#    cache.set("isFlagged", True)
#    return cache.get("isFlagged")

#Callback that toggles the alert of new anomalies.
@app.callback(
    Output("alertMsg", "is_open"),
    Input('interval-component', 'n_intervals'), 
    Input("goTo", "n_clicks"), 
    Input("dismis", "n_clicks"),
    State("alertMsg", "is_open"),
)
def toggle_alert(n1, n2, n3, is_open):
    triggered_id = ctx.triggered_id
    if triggered_id == 'interval-component':

        return check_for_new_anomalies(is_open)
    else: return not is_open

def check_for_new_anomalies(is_open):
    print(cache.get("isFlagged"))
    if cache.get("isFlagged"):
        cache.set("isFlagged", False)
        return True
    return is_open


#Debug true allows for hot reloading while writing code.
if __name__ == "__main__":
    app.run(debug=True)