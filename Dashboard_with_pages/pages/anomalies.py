from turtle import st
from dash import Dash, dcc, html, Input, Output, callback, dash_table, State, ctx
import pandas as pd
import dash
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import random
from plotly.graph_objs import *
from .testdata import genLists


dash.register_page(__name__)

# Not an actual page yet. Just for showing that pages can be changed.

testDf = pd.read_csv(r"Dashboard_with_pages\TestCSVLg.csv", delimiter=";")

buttonList = []
for i in testDf.index:
    buttonList.append("...")

testDf["..."] = buttonList


layout = html.Div(
    children=[
        html.Div(id="my-output"),
        html.Div(html.H1("Anomalies"), id="TitleDIV"),
        html.Div(
            # This breadcrumb is simply hardcoded for now. Should probably be fixed
            html.P("Homepage / page / page")
        ),
        html.Div(
            children=[
                # The datepicker is taken from the DCC page, and it's functionality is defined
                # in the callback in the bottom.
                dcc.DatePickerRange(
                    id="my-date-picker-range",
                    min_date_allowed=date(1995, 8, 5),
                    max_date_allowed=date(2017, 9, 19),
                    initial_visible_month=date(2017, 8, 5),
                    end_date=date(2017, 8, 25),
                ),
                html.Div(id="output-container-date-picker-range", style={}),
            ]
        ),
        html.Div(
            [
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Options")),
                        dbc.ModalBody(
                            html.Div(
                                children=[
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
                        dbc.ModalFooter(
                            children=[
                                dbc.Button(
                                    "OK", id="OK", className="ms-auto", n_clicks=0
                                ),
                                dbc.Button(
                                    "Close", id="close", className="ms-auto", n_clicks=0
                                ),
                            ]
                        ),
                    ],
                    id="modal",
                    is_open=False,
                ),
            ]
        ),
        html.Div(
            children=[
                html.H5("Anomalies", style={"margin-top": "20px"}),
                dash_table.DataTable(
                    testDf.to_dict("records"),
                    id="InboxTable",
                    columns=[{"name": i, "id": i} for i in testDf.columns],
                    editable=True,
                    sort_action="native",
                    sort_mode="multi",
                    style_table={
                        "overflow": "auto",
                        "height": "100%",
                        "width": "100%",
                        "marginBottom": "20px",
                    },
                    style_header={"backgroundColor": "#b3b3b3", "fontWeight": "bold"},
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


"""@callback(
    Output("modal", "is_open"),
    [Input("InboxTable", "active_cell"), Input("close", "n_clicks")],
    [State("InboxTable", "derived_viewport_data"), State("modal", "is_open")],
)
def cell_clicked(active_cell, data, n, is_open):
    if n:
        return not is_open
    if active_cell:
        row = active_cell["row"]
        col = active_cell["column_id"]

        if col == "...":  # or whatever column you want
            selected = data[row]["ID"]
            print(selected)

            return 1
        else:
            return 1"""


"""@callback(Output("dd-output-container", "children"), Input("demo-dropdown", "value"))
def update_output(value):
    print(value)
    return f"You have selected {value}"
"""


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
def toggle_modal(active_cell, n, ok, value, data, is_open):
    if active_cell:
        row = active_cell["row"]
        col = active_cell["column_id"]
        # print(ok)
        if "demo-dropdown" == ctx.triggered_id:
            return is_open
        if "OK" == ctx.triggered_id:
            selected = data[row]["ID"]
            print(selected)
            print(value)
            return not is_open
        if "close" == ctx.triggered_id:
            return (not is_open, value)
        elif col == "...":  # or whatever column you want
            return not is_open
