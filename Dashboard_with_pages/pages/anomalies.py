import json
from dash import Dash, dcc, html, Input, Output, callback, dash_table, State, ctx
import pandas as pd
import dash
import plotly.express as px
import dash_bootstrap_components as dbc
from plotly.graph_objs import *
import requests
from flask import request
from datetime import datetime, timedelta
import time
import keyCloakHandler

dash.register_page(__name__)


# Entire html is now moved into a serve_layout() method which allows for reloading data when refreshing the page.
def serve_layout():
    if keyCloakHandler.CurrentUser is not None and keyCloakHandler.CurrentUser.isLoggedIn() :
        actualDataDF = getDataDF()
        # Render the layout.
        return html.Div(
            children=[
                dcc.Location(id="locAnomaly"),
                html.Div(
                    # Anomalies page title
                    html.H1("Anomalies", className="FontBold"),
                    id="TitleDIV",
                ),
                html.Div(
                    # This is the breadcrumb, made using Boostrap.
                    # The current href's lead nowhere, but can be easily changed to do so.
                    html.Nav(
                        html.Ol(
                            className="breadcrumb",
                            children=[
                                html.Li(
                                    className="breadcrumb-item",
                                    children=[
                                        html.A(
                                            "Home",
                                            href="./home.py",
                                            style={
                                                "text-decoration": "none",
                                                "color": "#6c757d",
                                            },
                                        )
                                    ],
                                ),
                                html.Li(
                                    className="breadcrumb-item",
                                    children=[
                                        html.A(
                                            "Anomaly Detector",
                                            href="",
                                            style={
                                                "text-decoration": "none",
                                                "color": "#6c757d",
                                            },
                                        )
                                    ],
                                ),
                                html.Li(
                                    "Anomalies",
                                    className="breadcrumb-item active FontBold",
                                    style={"color": "black"},
                                ),
                            ],
                        ),
                    ),
                ),
                # Dropdown menu
                html.Div(
                    children=[
                        dcc.Dropdown(
                            [
                                "All time",
                                "Today",
                                "Yesterday",
                                "Last two days",
                                "Last 7 days",
                                "This month",
                            ],
                            "Today",
                            id="interval_picker_dropdown",
                            style={"width": "10vw"},
                        ),
                    ]
                ),
                # This is the popup menu that is shown when the user presses the ... button.
                html.Div(
                    [
                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle("Options")),
                                dbc.ModalBody(
                                    html.Div(
                                        children=[
                                            # This is the dropdown menu containing the options the user can choose
                                            # in regards to marking/unmarking false positives.
                                            dcc.Dropdown(
                                                [
                                                    "Mark as False Positive",
                                                    "Unmark as False Positive",
                                                ],
                                                "Mark as False Positive",
                                                id="demo-dropdown",
                                            ),
                                        ]
                                    ),
                                ),
                                # This is the buttons for the popup - OK to confirm the chosen marking of an anomaly/cancel to cancel.
                                dbc.ModalFooter(
                                    children=[
                                        html.A(
                                            dbc.Button(
                                                "OK",
                                                id="OK",
                                                className="ms-auto",
                                                n_clicks=0,
                                                href="/anomalies/",
                                            )
                                        ),
                                        dbc.Button(
                                            "Close",
                                            id="close",
                                            className="ms-auto",
                                            n_clicks=0,
                                        ),
                                    ]
                                ),
                            ],
                            id="modal",
                            is_open=False,
                        ),
                    ]
                ),
                # This Div includes the entire card (Navbar + Datatable).
                html.Div(
                    children=[
                        # Nav bar that includes an icon, three dropdown menu items, and a search bar.
                        html.Div(
                            children=[
                                html.I(
                                    className="bi bi-filter fa-2x cardLine IconBold",
                                    style={
                                        "float": "left",
                                        "margin-left": "5px",
                                        "margin-right": "15px",
                                        "margin-top": "-5px",
                                    },
                                ),
                                dbc.DropdownMenu(
                                    label="Status",
                                    toggle_style={
                                        "background": "#f8f8f8",
                                        "color": "black",
                                    },
                                    toggleClassName="border-white",
                                    direction="down",
                                    children=[
                                        dbc.DropdownMenuItem(
                                            "Status 1", id="status_one_option"
                                        ),
                                        dbc.DropdownMenuItem(
                                            "Status 2", id="status_two_option"
                                        ),
                                        dbc.DropdownMenuItem(
                                            "Status 3", id="status_three_option"
                                        ),
                                    ],
                                    className="cardLine",
                                    id="dropdownmenu_status",
                                    style={"margin-right": "8px"},
                                ),
                                dbc.DropdownMenu(
                                    label="Severity",
                                    toggle_style={
                                        "background": "#f8f8f8",
                                        "color": "black",
                                        "border": "#f8f8f8",
                                    },
                                    toggleClassName="",
                                    direction="down",
                                    children=[
                                        dbc.DropdownMenuItem(
                                            "Severity 1", id="severity_one_option"
                                        ),
                                        dbc.DropdownMenuItem(
                                            "Severity 2", id="severity_two_option"
                                        ),
                                        dbc.DropdownMenuItem(
                                            "Severity 3", id="severity_three_option"
                                        ),
                                    ],
                                    className="cardLine",
                                    id="dropdownmenu_status",
                                    style={"margin-right": "8px"},
                                ),
                                dbc.DropdownMenu(
                                    label=" Date detected",
                                    toggle_style={
                                        "background": "#f8f8f8",
                                        "color": "black",
                                    },
                                    toggleClassName="border-white",
                                    direction="down",
                                    children=[
                                        dbc.DropdownMenuItem(
                                            "Date 1", id="date_one_option"
                                        ),
                                        dbc.DropdownMenuItem(
                                            "Date 2", id="date_two_option"
                                        ),
                                        dbc.DropdownMenuItem(
                                            "Date 3", id="date_three_option"
                                        ),
                                    ],
                                    className="cardLine",
                                    id="dropdownmenu_status",
                                    style={"margin-right": "8px"},
                                ),
                                # Searchbar currently has no functionality. This can easily be implemented with callbacks.
                                dbc.Input(
                                    id="input",
                                    className="bi bi-search fa-2x cardLine",
                                    placeholder="Search for an anomaly...",
                                    type="text",
                                    style={
                                        "width": "25vw",
                                        "float": "right",
                                        "background": "#f8f8f8",
                                    },
                                ),
                            ],
                            style={"margin": "10px 10px 10px 10px"},
                        ),
                        # Anomalies datatable, includes styling of the table/cells.
                        dash_table.DataTable(
                            id="InboxTable",
                            columns=[
                                {
                                    "name": i,
                                    "id": i,
                                    "type": "numeric",
                                }
                                if i != "anomaly_score"
                                else {
                                    "name": i,
                                    "id": i,
                                    "type": "numeric",
                                    "format": {"specifier": ".4f"},
                                }
                                for i in actualDataDF.columns
                            ],
                            editable=False,
                            sort_action="native",
                            sort_by=[{"column_id": "id", "direction": "asc"}],
                            sort_mode="multi",
                            style_table={
                                "overflow": "auto",
                                "padding": "20px 20px 20px 20px",
                                "height": "70vh",
                                "marginBottom": "20px",
                            },
                            style_data_conditional=[
                                {
                                    "if": {
                                        "filter_query": '{false_positive} contains "true"',
                                        "column_id": "false_positive",
                                    },
                                    "backgroundColor": "#86dd6b",
                                },
                                {
                                    "if": {"column_id": "anomaly_score"},
                                    "format": {"specifier": ".4f"},
                                },
                                {
                                    "if": {
                                        "filter_query": '{false_positive} contains "false"',
                                        "column_id": "false_positive",
                                    },
                                    "backgroundColor": "#e37c8b",
                                },
                            ],
                            style_header_conditional=[
                                {
                                    "if": {"column_id": "log_message"},
                                    "textAlign": "left",
                                }
                            ],
                            style_header={
                                "background": "#f8f8f8",
                                "color": "black",
                                "fontWeight": "bold",
                                "textAlign": "center",
                            },
                            style_cell_conditional=[
                                {"if": {"column_id": a}, "textAlign": "center"}
                                for a in [
                                    "id",
                                    "log_time",
                                    "false_positive",
                                    "anomaly_score",
                                    "...",
                                ]
                            ],
                            style_data={
                                "whiteSpace": "normal",
                                "width": "100px",
                            },
                            style_cell={"textAlign": "left"},
                        ),
                    ],
                    className="card bg-white DropShadow",
                    style={
                        "margin": "15px",
                        "height": "8%",
                        "width": "70vw",
                        "display": "flex",
                        "justify-content": "center",
                    },
                ),
            ],
            # Style customization for the whole page container:
            style={
                "padding-left": "30px",
                "padding-top": "20px",
                "background-color": "#f0f3f6",
                "width": "80vw",
            },
        )
    else :
        return html.Div(
            children=[
                dcc.Location(id="locAnomaly"),
                html.Div(
                    # Anomalies page title
                    id="page-content",
                ),
                ],
        )


# Sets the layout to our serve_layout
layout = serve_layout


# This is the callback for the functionality that marks/unmarks false positives in the anomaly data.
@callback(
    Output("modal", "is_open"),
    [
        Input("InboxTable", "active_cell"),
        Input("close", "n_clicks"),
        Input("OK", "n_clicks"),
        Input("demo-dropdown", "value"),
    ],
    [State("InboxTable", "derived_viewport_data"), State("modal", "is_open")],
)

# This method handles what pressing on the '...' button does.
# It intially checks if the user has clicked on a cell in the dataframe,
# and in that case whether or not that cell is a '...' cell
# If it is a '...' cell it opens a popup and allows the user to choose the desired outcome
# It uses an api call to update the database with the desired data
# 'n' and 'ok' are unused but needed due to callback syntax
def openMarkerPopUp(active_cell, n, ok, value, data, is_open):
    if active_cell:
        row = active_cell["row"]
        col = active_cell["column_id"]
        if "demo-dropdown" == ctx.triggered_id:
            return is_open
        if "OK" == ctx.triggered_id:
            selected = data[row]["id"]
            if value == "Mark as False Positive":
                value = True
            else:
                value = False
            requests.put(
                "http://localhost:8002/anomalies/Update_false_positive",
                params={"uId": selected, "uFalse_Positive": value},
            )
            return not is_open
        if "close" == ctx.triggered_id:
            return not is_open
        elif col == "...":
            return not is_open
        elif col == "log_message":
            return is_open


def calculate_interval(value):
    today = pd.Timestamp("today").floor("D")
    match value:
        case "Today":
            return (today, today)
        case "Yesterday":
            return (today + pd.offsets.Day(-1), today + pd.offsets.Day(-1))
        case "Last two days":
            return (today, today + pd.offsets.Day(-1))
        case "Last 7 days":
            return (today, today + pd.offsets.Day(-6))
        case "This month":
            return (today, today + pd.offsets.MonthEnd(-1))
        case "All time":
            return (today, pd.Timestamp(year=1999, month=1, day=1))


# Method for updating dataframe
# When an option is selected in the dropdown the table is updated to fit the filter
# When the ok button is clicked we also update the table
@callback(
    Output("InboxTable", component_property="data"),
    [Input("interval_picker_dropdown", "value"), Input("OK", "n_clicks")],
)
def adjust_table(value, n):
    time.sleep(0.1)
    if value:
        actualDataDF = getDataDF()
        interval = calculate_interval(value)

        copyDf = actualDataDF[
            (actualDataDF["log_time"] <= interval[0])
            & (actualDataDF["log_time"] >= interval[1])
        ]
        return copyDf.to_dict(orient="records")
    elif n:
        return getDataDF().to_dict(orient="records")


# This method gets and creates/recreates the dataframe with data from the database.
def getDataDF():
    data = requests.get("http://localhost:8002/anomalies/get_anomaly_list").json()
    jsonData = json.dumps(data)
    actualDataDF = pd.read_json(jsonData)
    actualDataDF = actualDataDF.reindex(
        columns=["id", "log_message", "log_time", "false_positive", "anomaly_score"]
    )
    buttonList = []
    for i in actualDataDF.index:
        buttonList.append("...")
    actualDataDF["..."] = buttonList
    pd.options.display.width = 10
    return actualDataDF

@callback(
    Output('locAnomaly', 'href'),
    Input('page-content', 'children'),
    allow_duplicate=True)
def toLogin(input):
    return "http://127.0.0.1:8050/login"