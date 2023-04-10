from dash import Dash, dcc, html, Input, Output, State
import dash
import pandas as pd
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import random
from plotly.graph_objs import *
import requests

##The app.py page does not actually contain the pages that are being loaded, it is more so a container
#for pages. It only contains the sidebar (containing buttons to navigate) and a page_container.
#The page container then loads the actual pages from the pages directory.
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], use_pages=True)


app.layout = html.Div(children=[ 

    html.Div(id="Sidebar",children=[
        html.Div(children=[
            html.H2("SYSTEMATIC",className="FontLogo",id="Logo"),

            ##The modal button is only for showing a pop up and the callback associated with a pop up.
            #It should be deleted at some point.
            dbc.Button("Modal", color="primary",id="ModalBTN"),
            html.Div(
                html.H5("Anomaly Detector", className="FontMain FontWhite SideElement")
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
                dbc.Button(f" {page['name']}", color="secondary",class_name="SideBTN SideElement bi bi-house",href=page["relative_path"]),
                style={"margin-top" : "5vh","margin-left" : "2%","font-weight" : "500"},
            )
            for page in dash.page_registry.values()
        ]
    ),

    ]),




    html.Div(id="Main-panel",children=[

            dash.page_container

    ])], style={"display":"flex","width" : "100vw"}
    )


def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

app.callback(
    Output("modal-sm", "is_open"),
    Input("ModalBTN", "n_clicks"),
    State("modal-sm", "is_open"),
)(toggle_modal)

#Debug true allows for hot reloading while writing code.
if __name__ == "__main__":
    app.run(debug=True)