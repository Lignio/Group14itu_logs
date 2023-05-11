from dash import Dash, dcc, html, Input, Output, callback, dash_table, State
import pandas as pd
import dash
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import requests
from plotly.graph_objs import *
import json
import keyCloakHandler

# Separate pages need to be registered like this to show up in the page container in app.py
dash.register_page(__name__)

def serve_layout():
    #div that cover the whole side
        return html.Div([
            html.Div(id="hiddenDiv",style={"display":"none"}),
            dcc.Location(id="location"),
            dbc.Col([
                html.H2("Log in", className="SideElement", style={"margin":"5vh"}),
                dbc.FormFloating(
                        [
                            dbc.Input(placeholder="example@internet.com", id="userForm"),
                            dbc.Label("Username"),
                        ],
                        style={"width": "50%","padding-bottom":"5vh"},
                        className="SideElement",
                    ),
                dbc.FormFloating(
                    [
                        dbc.Input(
                            type="password",
                            placeholder="example@internet.com",
                            id="passForm",
                        ),
                        dbc.Label("Password"),
                    ],
                    style={"width": "50%","padding-bottom":"5vh"},
                    className="SideElement",
                ),
                dbc.Button(
                    "Login",
                    className="SideBTN SideElement bi bi-box-arrow-in-right",
                    style={"vertical-align": "text-bottom",},
                    id="LoginBTN",
                    n_clicks=0
                )
            ],className='loginCard'),   
        ],className="centered SystematicGradient"
)

layout= serve_layout()

@callback(
    Output("location","href"),
    Input("LoginBTN","n_clicks"),
    [State("userForm", "value"),
    State("passForm", "value")],
    prevent_initial_call=True,
)
def prints(n,userN,userP):
    keyCloakHandler.CurrentUser = keyCloakHandler.currentUserSession(userN, userP)
    return "http://127.0.0.1:8050/"


 