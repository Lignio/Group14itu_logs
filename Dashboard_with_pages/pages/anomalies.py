import json
from turtle import st
from dash import Dash, dcc, html, Input, Output, callback, dash_table, State, ctx
import pandas as pd
import dash
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import random
from plotly.graph_objs import *
import requests
from flask import request
from pages.testdata import genLists
from datetime import datetime, timedelta


dash.register_page(__name__)


def serve_layout():
    actualDataDF = getDataDF()
    # Render the layout.
    return html.Div(
        children=[
            # dcc.Location(id='url'),
            html.Div(html.H1("Anomalies"), id="TitleDIV"),
            html.Div(
                # This breadcrumb is simply hardcoded for now. Should probably be fixed
                html.P("Homepage / page / page")
            ),
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
                            # This is the closing buttons for the popup - OK to confirm the chosen marking of an anomaly/cancel to cancel.
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
            # This is the div containing the anomalies data
            html.Div(
                children=[
                    html.H5("Anomalies", style={"margin-top": "20px"}),
                    dash_table.DataTable(
                        id="InboxTable",
                        columns=[{"name": i, "id": i} for i in actualDataDF.columns],
                        editable=False,
                        sort_action="native",
                        sort_mode="multi",
                        style_table={
                            "overflow": "auto",
                            "height": "100%",
                            "width": "100%",
                            "marginBottom": "20px",
                        },
                        style_header={
                            "backgroundColor": "#b3b3b3",
                            "fontWeight": "bold",
                        },
                        style_data={
                            "whiteSpace": "normal",
                            "width": "100px",
                            "textAlign": "left",
                        },
                    ),
                ],
                style={
                    "margin": "15px",
                    "background-color": "#e0e0d1",
                    "height": "8%",
                    "width": "70vw",
                    "outline-color": "#b7b795",
                    "outline-style": "solid",
                    "outline-width": "3px",
                },
            ),
        ],
        style={"margin-left": "20px"},
    )


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

# This is the "method" that handles what pressing on the ... does.
# It iintially checks if the user has clicked on a cell in the dataframe,
# and in that case whether or not that cell is a ... cell
# If it is a ... cell it opens the popup and allow the user to choose desired outcome.
def openMarkerPopUp(active_cell, n, ok, value, data, is_open):
    if active_cell:
        row = active_cell["row"]
        col = active_cell["column_id"]
        # print(ok)
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
            print(selected)
            print(value)
            return not is_open
        if "close" == ctx.triggered_id:
            return not is_open
        elif col == "...":  # or whatever column you want
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


# When an option is selected in the dropdown the table is updated to fit the filter
@callback(
    Output("InboxTable", component_property="data"),
    Input("interval_picker_dropdown", "value"),
)
def adjust_table_to_interval(value):
    actualDataDF = getDataDF()
    interval = calculate_interval(value)

    copyDf = actualDataDF[
        (actualDataDF["log_time"] <= interval[0])
        & (actualDataDF["log_time"] >= interval[1])
    ]
    return copyDf.to_dict(orient="records")


def getDataDF():
    data = requests.get("http://localhost:8002/anomalies/get_anomaly_list").json()
    jsonData = json.dumps(data)
    actualDataDF = pd.read_json(jsonData)
    actualDataDF = actualDataDF.reindex(
        columns=["id", "log_message", "log_time", "anomaly_score", "false_positive"]
    )
    buttonList = []
    for i in actualDataDF.index:
        buttonList.append("...")
    actualDataDF["..."] = buttonList
    pd.options.display.width = 10
    return actualDataDF


"""@callback(Output('url', 'pathname'),
              [Input('OK', 'n_clicks')],
              [State('url', 'pathname')])
def navigate_to_anomalies(n_clicks, pathname):
    if n_clicks:
        return pathname"""
