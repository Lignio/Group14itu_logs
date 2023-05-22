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
from pydantic import BaseSettings
from loguru import logger
import pages.dashboard as dashboard


class Settings(BaseSettings):
    controller: str


settings = Settings()

controller = settings.controller

get_anomaly_list = f"{controller}/get_anomaly_list"
update_false_positive = f"{controller}/Update_false_positive"
mark_as_handled = f"{controller}/Mark_as_handled"


dash.register_page(__name__)


# Entire html is now moved into a serve_layout() method which allows for reloading data when refreshing the page.
def serve_layout():
    if (
        keyCloakHandler.CurrentUser is not None
        and keyCloakHandler.CurrentUser.isLoggedIn()
    ):
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
                                dbc.ModalHeader(dbc.ModalTitle("Options"), close_button=False),
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
                                # Dropdown for choosing which severity level to filter by
                                dcc.Dropdown(
                                    [
                                        "Low Severity",
                                        "Medium Severity",
                                        "High Severity",
                                        "Any Severity",
                                    ],
                                    "Any Severity",
                                    id="dropdownmenu_severity",
                                    className="cardLine",
                                    style={"width": "13vw", "margin-right": "8px"},
                                ),
                                dcc.Dropdown(
                                    [
                                        "Unhandled Anomalies",
                                        "Handled Anomalies",
                                        "All Anomalies",
                                    ],
                                    "Unhandled Anomalies",
                                    id="dropdownmenu_handled",
                                    className="cardLine",
                                    style={"width": "13vw", "margin-right": "8px"},
                                ),
                            ],
                            style={"margin": "10px 10px 10px 10px", "display": "flex"},
                        ),
                        # Anomalies datatable, includes styling of the table/cells.
                        dash_table.DataTable(
                            id="anomaly_table",
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
                            hidden_columns=["is_handled"],
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
                            tooltip_conditional = [
                                {
                                    'if': {'column_id': col},
                                    'value': 'Click to edit this value',
                                    'use_with': 'data'
                                } for col in ['false_positive', '...']
                            ],
                            tooltip_delay=0,
                            tooltip_duration=None,
                            css=[{"selector": ".show-hide", "rule": "display: none"},
                                 {'selector': '.dash-table-tooltip', 'rule': 'background-color: #141446; color: white'}],
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
                                {
                                    "if": {
                                        "filter_query": '{false_positive} contains "false"',
                                        "column_id": "false_positive",
                                    },
                                    "backgroundColor": "#e37c8b",
                                },
                                {
                                    "if": {
                                        "filter_query": '{severity} contains "low"',
                                        "column_id": "severity",
                                    },
                                    "backgroundColor": "#FFFF00",
                                },
                                {
                                    "if": {
                                        "filter_query": '{severity} contains "medium"',
                                        "column_id": "severity",
                                    },
                                    "backgroundColor": "#ffa500",
                                },
                                {
                                    "if": {
                                        "filter_query": '{severity} contains "high"',
                                        "column_id": "severity",
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
                                    "severity",
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
    else:
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
    Output("anomaly_table", "active_cell"),
    [
        Input("anomaly_table", "active_cell"),
        Input("close", "n_clicks"),
        Input("OK", "n_clicks"),
        Input("demo-dropdown", "value"),
    ],
    [State("anomaly_table", "derived_viewport_data"), State("modal", "is_open")],
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
                update_false_positive,
                params={"uId": selected, "uFalse_Positive": value},
            )
            requests.put(mark_as_handled, params={"uId": selected})
            return not is_open, None
        if "close" == ctx.triggered_id:
            return not is_open, None
        elif (col == "...") or (col == "false_positive"):
            return not is_open, active_cell
        elif col == "log_message":
            return is_open, active_cell


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
            return ("2024-01-01", pd.Timestamp(year=1999, month=1, day=1))


# Matches the input value with which severity to return
def severity_interval(value):
    match value:
        case "Low Severity":
            return "low"
        case "Medium Severity":
            return "medium"
        case "High Severity":
            return "high"


def handled_value(value):
    match value:
        case "Unhandled Anomalies":
            return False
        case "Handled Anomalies":
            return True


# Method for updating dataframe
# When an option is selected in the dropdown the table is updated to fit the filter
# When the ok button is clicked we also update the table
@callback(
    Output("anomaly_table", component_property="data"),
    [
        Input("interval_picker_dropdown", "value"),
        Input("OK", "n_clicks"),
        Input("dropdownmenu_severity", "value"),
        Input("dropdownmenu_handled", "value"),
    ],
)
def adjust_table(value, n, sevValue, hanValue):
    data = getCopyDF(value)

    container = dashboard.dataContainer
    id = container.id
    # Checks if we only need to show the anomaly chosen in the anomaly inbox on the dashboard
    # If that is the case, selects the id of that anomanly and only displays that in the datatable
    if id != 0:
        data = getSpecificAnomaly(id)
        dashboard.dataContainer.id = 0
        return data.to_dict(orient="records")

    # Checks if it needs to filter by severity and if yes, which severity
    elif sevValue != "Any Severity":
        # Checks if a specific filter for if anomalies has been handled or not
        # and adjusts the datatable as neccesary
        if hanValue != "All Anomalies":
            newData = getHandledDF(hanValue, data)
            severity = severity_interval(sevValue)
            actualData = newData[(newData["severity"] == severity)]
            return actualData.to_dict(orient="records")
        severity = severity_interval(sevValue)
        actualData = data[(data["severity"] == severity)]
        return actualData.to_dict(orient="records")

    elif value:
        if hanValue != "All Anomalies":
            newData = getHandledDF(hanValue, data)
            return newData.to_dict(orient="records")
        return data.to_dict(orient="records")

    elif n:
        data = getCopyDF(value)
        return data(orient="records")


# This method gets and creates/recreates the dataframe with data from the database.
def getDataDF():
    data = requests.get(get_anomaly_list).json()
    jsonData = json.dumps(data)
    actualDataDF = pd.read_json(jsonData, convert_dates=False)
    actualDataDF = actualDataDF.reindex(
        columns=[
            "id",
            "log_message",
            "log_time",
            "false_positive",
            "anomaly_score",
            "is_handled",
        ]
    )
    actualDataDF["log_time"] = pd.to_datetime(
        actualDataDF["log_time"], format="%d/%m/%Y", dayfirst=True
    )

    severityList = []
    for i in actualDataDF.anomaly_score:
        if i < 0.03:
            severityList.append("low")
        elif i < 0.05:
            severityList.append("medium")
        else:
            severityList.append("high")
    actualDataDF["severity"] = severityList

    buttonList = []
    for i in actualDataDF.index:
        buttonList.append("...")
    actualDataDF["..."] = buttonList

    pd.options.display.width = 10
    return actualDataDF


@callback(
    Output("locAnomaly", "href"),
    Input("page-content", "children"),
    allow_duplicate=True,
)
def toLogin(input):
    return "http://127.0.0.1:8050/login"


# Method for getting updated dataframe based on date-filtering
def getCopyDF(value):
    actualDataDF = getDataDF()
    interval = calculate_interval(value)

    copyDf = actualDataDF[
        (actualDataDF["log_time"] <= interval[0])
        & (actualDataDF["log_time"] >= interval[1])
    ]

    return copyDf


# Method for getting updated dataframe based on filtering on (un)handled anomalies
def getHandledDF(value, dataFrame):
    handledVal = handled_value(value)
    newDF = dataFrame[(dataFrame["is_handled"] == handledVal)]

    return newDF


# Method for getting a dataframe with only 1 anomaly in based on it's id
def getSpecificAnomaly(id):
    data = getDataDF()
    actualData = data[(data["id"] == id)]
    return actualData
