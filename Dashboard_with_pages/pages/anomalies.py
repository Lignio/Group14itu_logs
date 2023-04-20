from turtle import st
from dash import Dash, dcc, html, Input, Output, callback, dash_table, State, ctx
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
originalDF = pd.read_csv("Dashboard_with_pages\TestCSVLg.csv", delimiter=";")
originalDF["Date"] = pd.to_datetime(
    originalDF["Date"], format="%d/%m/%Y", dayfirst=True
)

# Appends the ... button to the dataframe containing the data from the database
# This is currently using data from the  TestCSVLg file.
buttonList = []
for i in originalDF.index:
    buttonList.append("...")

originalDF["..."] = buttonList

layout = html.Div(children=[
    html.Div(
            #Anomilies page title
            html.H1("Anomalies", className="FontBold"),
            id="TitleDIV"
        ),
        html.Div(
            #This is the breadcrumb, made using Boostrap.
            #The current href's lead nowhere, but can be easily changed to do so.
            html.Nav(
                html.Ol(className="breadcrumb", children=[
                    html.Li(className="breadcrumb-item", children=[
                        html.A("Home", href="./home.py", style={"text-decoration":"none", "color":"#6c757d"})
                    ]),
                    html.Li(className="breadcrumb-item", children=[
                        html.A("Anomaly Detector", href="", style={"text-decoration":"none", "color":"#6c757d"})
                    ]),
                    html.Li("Anomalies", className="breadcrumb-item active FontBold", style={"color":"black"})
                ])
            )
        ),
        #Dropdown menu
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
                    style={"width":"10vw"}
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
        # This Div includes the entire card (Navbar + Datatable).
        html.Div(children=[
                    #Nav bar, includes icon, three dropdown menu and a search bare.
                    html.Div(children=[
                        html.I(className="bi bi-filter fa-2x cardLine IconBold", style={"float":"left", "margin-left":"5px","margin-right":"15px","margin-top":"-5px"}),
                        dbc.DropdownMenu(
                            label="Status", 
                            toggle_style={"background":"#f8f8f8", "color":"black"}, 
                            toggleClassName="border-white",
                            direction="down",
                            children=[
                                dbc.DropdownMenuItem("Status 1", id="status_one_option"),
                                dbc.DropdownMenuItem("Status 2", id="status_two_option"),
                                dbc.DropdownMenuItem("Status 3", id="status_three_option" )
                                ], className="cardLine", id="dropdownmenu_status",style={"margin-right":"8px"}),
                        dbc.DropdownMenu(
                            label="Severity", 
                            toggle_style={"background":"#f8f8f8", "color":"black","border":"#f8f8f8"}, 
                            toggleClassName="",
                            direction="down",
                            children=[
                                dbc.DropdownMenuItem("Severity 1", id="severity_one_option"),
                                dbc.DropdownMenuItem("Severity 2", id="severity_two_option"),
                                dbc.DropdownMenuItem("Severity 3", id="severity_three_option" )
                                ], className="cardLine", id="dropdownmenu_status",style={"margin-right":"8px"}),
                        dbc.DropdownMenu(
                            label=" Date detected", 
                            toggle_style={"background":"#f8f8f8", "color":"black"}, 
                            toggleClassName="border-white",
                            direction="down",
                            children=[
                                dbc.DropdownMenuItem("Date 1", id="date_one_option"),
                                dbc.DropdownMenuItem("Date 2", id="date_two_option"),
                                dbc.DropdownMenuItem("Date 3", id="date_three_option" )
                                ], className="cardLine", id="dropdownmenu_status",style={"margin-right":"8px"}),
                            #Searchbar currently has not functionality. This can easily be done with callbacks.
                            dbc.Input(id="input", className="bi bi-search fa-2x cardLine", placeholder="Search for an anomaly...", type="text",
                                    style={"width":"25vw","float":"right","background":"#f8f8f8"})
                        ,
                        
                    ], style={"margin":"10px 10px 10px 10px"}),
                #Anomilies datatable
                dash_table.DataTable(
                    id="InboxTable",
                    columns=[{"name": i, "id": i} for i in originalDF.columns],
                    editable=True,
                    sort_action="native",
                    sort_mode="multi",
                    style_table={
                        "overflow": "auto",
                        'padding' : '20px 20px 20px 20px',
                        'height' : '70vh',
                        "marginBottom": "20px",
                    },
                    style_header={
                        'background' : '#f8f8f8',
                        'color' : 'black',
                        'fontWeight': 'bold'},
                ),
            ],className="card bg-white DropShadow",
            style={"margin":"15px","height":"8%","width":"70vw","display" : "flex", "justify-content" : "center"}
        ),
    ],
    #Style customization for the whole page container:
    style={"padding-left":"30px","padding-top":"20px","background-color":"#f0f3f6","width":"80vw"})
    


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
            selected = data[row]["ID"]
            print(selected)
            print(value)
            return not is_open
        if "close" == ctx.triggered_id:
            return not is_open
        elif col == "...":  # or whatever column you want
            return not is_open


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
    interval = calculate_interval(value)

    copyDf = originalDF[
        (originalDF["Date"] <= interval[0]) & (originalDF["Date"] >= interval[1])
    ]
    return copyDf.to_dict(orient="records")