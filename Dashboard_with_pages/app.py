from dash import Dash, dcc, html, Input, Output, State, ctx
import dash
import pandas as pd
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
from plotly.graph_objs import *
import requests

# import keyCloakHandler
# from pydantic import BaseSettings


# class Settings(BaseSettings):
#    controller: str

# settings = Settings()

# controller = settings.controller

# check_flag = f"{controller}/checkFlag"

##The app.py page does not actually contain the pages that are being loaded, it is more so a container
# for pages. It only contains the sidebar (containing buttons to navigate) and a page_container.
# The page container then loads the actual pages from the pages directory.
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    use_pages=True,
)


app.layout = html.Div(
    children=[
        html.Div(
            id="Sidebar",
            children=[
                dcc.Interval(id="interval-component", interval=1 * 5000, n_intervals=0),
                html.Div(
                    children=[
                        html.H2("SYSTEMATIC", className="FontLogo", id="Logo"),
                        ##The modal button is only for showing a pop up and the callback associated with a pop up.
                        # It should be deleted at some point.
                        html.Div(
                            html.H5(
                                "Anomaly Detector",
                                className="FontMain FontWhite SideElement",
                            )
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            dbc.Button(
                                f" {page['name']}",
                                color="secondary",
                                class_name="SideBTN SideElement bi bi-kanban",
                                href=page["relative_path"],
                            )
                            if "Dashboard" in f" {page['name']}"
                            else dbc.Button(
                                f" {page['name']}",
                                color="secondary",
                                class_name="SideBTN SideElement bi bi-exclamation-circle",
                                href=page["relative_path"],
                            ),
                            style={
                                "margin-top": "5vh",
                                "margin-left": "2%",
                                "font-weight": "500",
                            },
                        )
                        for page in dash.page_registry.values()
                    ]
                ),
            
                
            ],
        ),
        html.Div(id="Main-panel", children=[dash.page_container]),
        dbc.Alert(
            [
                html.H4(
                    "New anomaly detected",
                    className="alert-heading",
                ),
                html.P("Choose to review it now or later"),
                html.Div(
                    [
                        dbc.Button(
                            "Dismiss",
                            id="dismiss",
                            className=" alertBtn",
                            style={"float": "left"},
                        ),
                        dbc.Button(
                            "Go to anomaly",
                            id="goTo",
                            className="alertBtn",
                            n_clicks=0,
                            href="/anomalies",
                            style={"float": "right"},
                        ),
                    ],
                    id="alertBtnContainer",
                ),
            ],
            id="alertMsg",
            color="light",
            is_open=False,  # Not sure if this line should be here.
        ),
    ],
    style={"display": "flex", "width": "100vw"},
)


# Callback that toggles the alert of new anomalies.
@app.callback(
    Output("alertMsg", "is_open"),
    Input("interval-component", "n_intervals"),
    Input("goTo", "n_clicks"),
    Input("dismiss", "n_clicks"),
    State("alertMsg", "is_open"),
)
def toggle_alert(n1, n2, n3, is_open):
    triggered_id = ctx.triggered_id
    if triggered_id == "interval-component":
        return check_for_new_anomalies(is_open)
    else:
        return not is_open


def check_for_new_anomalies(is_open):
    # isFlagged = requests.get(check_flag).json()  # Calls checkFlag in Controller
    isFlagged = requests.get("http://localhost:8002/check_flag")
    if isFlagged:
        return True
    return is_open







# Debug true allows for hot reloading while writing code.
if __name__ == "__main__":
    app.run(debug=True)
