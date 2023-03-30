from turtle import st
from dash import Dash, dcc, html, Input, Output, callback, dash_table, State
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
            children=[
                dcc.Dropdown(
                    ["Mark as False Positive", "MTL", "SF"],
                    "Mark as False Positive",
                    id="demo-dropdown",
                ),
                html.Div(id="dd-output-container"),
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


@callback(
    Output("my-output", "children"),
    Input("InboxTable", "active_cell"),
    State("InboxTable", "derived_viewport_data"),
)
def cell_clicked(active_cell, data):
    if active_cell:
        row = active_cell["row"]
        col = active_cell["column_id"]

        if col == "...":  # or whatever column you want
            selected = data[row]["ID"]
            print(selected)
            return 1
        else:
            return 1


@callback(Output("dd-output-container", "children"), Input("demo-dropdown", "value"))
def update_output(value):
    print(value)
    return f"You have selected {value}"
