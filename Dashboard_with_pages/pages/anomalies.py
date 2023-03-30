from turtle import st
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import dash
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import random
from plotly.graph_objs import *
from pages.testdata import genLists
from datetime import datetime, timedelta


dash.register_page(__name__)

# Not an actual page yet. Just for showing that pages can be changed.
orinalDf = pd.read_csv("Dashboard_with_pages\TestCSVLg.csv", delimiter=";")
copyDf = orinalDf


layout = html.Div(
    children=[
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
                        "This week",
                    ],
                    "Today",
                    id="interval_picker_dropdown",
                ),
                html.Div(id="interval_output"),
            ]
        ),
        html.Div(
            children=[
                html.H5("Anomalies", style={"margin-top": "20px"}),
                dash_table.DataTable(
                    copyDf.to_dict("records"),
                    id="InboxTable",
                    columns=[{"name": i, "id": i} for i in copyDf.columns],
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


def calculate_interval(value):
    today = date.today()
    match value:
        case "Today":
            return (today, today)
        case "Yesterday":
            return (today - timedelta(days=1), today - timedelta(days=1))
        case "Last two days":
            return (today, today - timedelta(days=1))
        case "This week":
            return (today, today - timedelta(days=6))


def is_in_interval(interval, dateDiscovered):
    return interval[0] <= dateDiscovered <= interval[1]


@callback(
    Output("interval_output", "children"), Input("interval_picker_dropdown", "value")
)
def adjust_table_to_interval(value):
    interval = calculate_interval(value)

    copyDf = orinalDf[is_in_interval(interval, orinalDf.Date)]
    return 0
