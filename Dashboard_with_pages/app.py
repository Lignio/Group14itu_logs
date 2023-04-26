from operator import is_
from pydoc import classname
from dash import Dash, dcc, html, Input, Output, State
import dash
import pandas as pd
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import random
from plotly.graph_objs import *
import requests
import keyCloakHandler

##The app.py page does not actually contain the pages that are being loaded, it is more so a container
#for pages. It only contains the sidebar (containing buttons to navigate) and a page_container.
#The page container then loads the actual pages from the pages directory.
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], use_pages=True)

#keyCloakHandler.logoutUser(userauthtoken)

app.layout = html.Div(children=[ 

    html.Div(id="Sidebar",children=[
        html.Div(children=[
            html.H2("SYSTEMATIC",className="FontLogo",id="Logo"),

            ##The modal button is only for showing a pop up and the callback associated with a pop up.
            #It should be deleted at some point.
            dbc.Button("Modal", color="primary",id="ModalBTN"),
            html.Div(
                html.H5("Anomaly Detector", className="FontMain FontWhite SideElement"),
                
            ),
            ##The modal is the popup alerting the users of new anomalies. So far we believe that
            #the actual location of the modal doesn't matter, as it always pops up in the same place.
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Header")),
                    dbc.ModalBody("A small modal."),
                ],
                id="modal-sm",
                size="sm",
                is_open=False,
                )
            ]),
        html.Div(children=[
            html.Div(
                dbc.Button(f" {page['name']}", color="secondary",class_name="SideBTN SideElement bi bi-kanban",href=page["relative_path"])if "Dashboard" in f" {page['name']}"
                else dbc.Button(f" {page['name']}", color="secondary",class_name="SideBTN SideElement bi bi-exclamation-circle",href=page["relative_path"]),
                style={"margin-top" : "5vh","margin-left" : "2%","font-weight" : "500"},
            )
            for page in dash.page_registry.values()
            
        ]
        ),

        # Tempoary login forms, shouldn't be here in the long run
        dbc.FormFloating([
            dbc.Input(placeholder="example@internet.com",id="userForm"),
            dbc.Label("Email address"),
        ],style={"width":"80%"},className="SideElement"),
        dbc.FormFloating([
            dbc.Input(type="password",placeholder="example@internet.com",id="passForm"),
            dbc.Label("Password"),
        ],style={"width":"80%"},className="SideElement"),
        dbc.Button(" Login", className="SideBTN SideElement bi bi-box-arrow-in-right", style={"vertical-align":"text-bottom"},id="LoginBTN"),
        # Fade component lets the card fade in when you're logged in, and is hidden when you're not initially
        # logged in.
        dbc.Fade(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Card title", className="card-title", id="UserNameCardTitle",style={"margin-left":"55px"}),
                    
                    dbc.Button("Log out", id="logoutBTN",className="SideBTN SideElement bi bi-box-arrow-in-right"),
                    ]),
                className="mb-3 SideElement",
                style={"width":"70%","margin-top":"10px"}
            ),
        id="fade",
        is_in=False,
        appear=False,
        )
        

    ]),




    html.Div(id="Main-panel",children=[

            dash.page_container

    ])], style={"display":"flex","width" : "100vw"}
    )


def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

def getUserInfo():
    info = keyCloakHandler.getUserInfo("jskoven","123")
    username = info["preferred_username"]
    return username


app.callback(
    Output("modal-sm", "is_open"),
    Input("ModalBTN", "n_clicks"),
    State("modal-sm", "is_open"),
)(toggle_modal)

@app.callback(
    Output("UserNameCardTitle","children"),
    Input("LoginBTN", "n_clicks"),
    Input("userForm","value"),
    Input("passForm","value"),
    Input("logoutBTN","n_clicks"),
    prevent_initial_call=True
)
def setUsername(n_clicks, userN, pw, n_clicks2):
    if n_clicks != 0:
        ctx = dash.callback_context
        if "LoginBTN" == ctx.triggered_id:
            info = keyCloakHandler.getUserInfo(userN,pw)
            if info["preferred_username"] is not None and userN is not None and pw is not None:
                return info["preferred_username"]
        if "logoutBTN" == ctx.triggered_id:
            return "Logged out"
        


@app.callback(
    Output("fade", "is_in"),
    [Input("LoginBTN", "n_clicks")],
    [State("fade", "is_in")],   
)
def toggle_fade(n, is_in):
    if not n:
        # Button has never been clicked
        return False
    return True


#Debug true allows for hot reloading while writing code.
if __name__ == "__main__":
    app.run(debug=True)