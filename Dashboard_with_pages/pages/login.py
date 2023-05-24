from dash import Dash, dcc, html, Input, Output, callback, dash_table, State
import pandas as pd
import dash
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import requests
import plotly.graph_objs
import json
import keyCloakHandler
from dash.exceptions import PreventUpdate

# Separate pages need to be registered like this to show up in the page container in app.py
dash.register_page(__name__)


def serve_layout():
    # div that cover the whole side
    return html.Div(
        [
            html.Div(id="hiddenDiv", style={"display": "none"}),
            dcc.Location(id="location"),
            dbc.Col(
                [
                    html.H2("Log in", className="SideElement", style={"margin": "5vh"}),
                    dbc.FormFloating(
                        [
                            dbc.Input(
                                placeholder="example@internet.com", id="userForm"
                            ),
                            dbc.Label("Username"),
                        ],
                        style={"width": "50%", "padding-bottom": "5vh"},
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
                    style={"vertical-align": "text-bottom","margin-bottom":"2vh",},
                    id="LoginBTN",
                    n_clicks=0
                ),
                #Prompt for when login failed - will only show when necessary
                html.Div([
                    html.P("Incorrect username or password", className="SideElement error-text"), 
                ],id='loginFailedBox',className="shakeAnimation SideElement form-floating error-message",style={"display":"none"},
                ),
            ],className='loginCard'),      
        ],className="centered SystematicGradient"
)

@callback(
    [
        Output("location", "href"),
        Output(component_id="loginFailedBox", component_property="style"),
    ],
    [
        Input("LoginBTN", "n_clicks"),
        Input("passForm", "n_submit"),
        Input("userForm", "n_submit"),
    ],
    [State("userForm", "value"), State("passForm", "value")],
    prevent_initial_call=True,
)
# Checks if the user can log in or not
# If no user is found prompt will be shown and no redirect will happen
def check_login_information(n, enter_press_pass, enter_press_user, userN, userP):
    try:
        keyCloakHandler.CurrentUser = keyCloakHandler.currentUserSession(userN, userP)
        return "http://127.0.0.1:8050/", {"display": "none"}
    except:  # invalid_user_credentials
        return dash.no_update, {"display": "block"}
        # raise PreventUpdate
