from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import dash
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import random
import requests
from plotly.graph_objs import *
from pages.testdata import genLists

# Separate pages need to be registered like this to show up in the page container in app.py
dash.register_page(__name__)

dataList = [["A", 1], ["B", 2], ["C", 3]]
anomalyScoreList = []

for i in dataList:
    anomalyScoreList.append(i[1])

anomalyToPiechart = [0, 0, 0]


def countvalues():
    for i in anomalyScoreList:
        if i < 0.024:
            anomalyToPiechart[0] += 1
        elif i > 0.024 and i < 0.026:
            anomalyToPiechart[1] += 1
        else:
            anomalyToPiechart[2] += 1
    print(anomalyToPiechart)
    return anomalyToPiechart


lst1, lst2 = genLists()

# The figures are currently just populated with test data. The figures are created
# with the plotly package, so all documentation is via plotly.
ScatterPlotFig = px.scatter(
    x=lst1, y=lst2, title="Scatter plot of name lengths"
).update_layout(
    xaxis_title="Name length",
    yaxis_title="Name count",
    margin=dict(l=20, r=20, t=30, b=20),
)
PieChartFig = px.pie(
    values=countvalues(),
    names=["0.02 - 0.024", "0.024 - 0.026", ">0.026"],
    title="Piechart for data",
).update_layout(margin=dict(l=20, r=20, t=30, b=20))

testDf = pd.read_csv("TestCSVLg.csv", delimiter=";")

# Layout = html.Div defines the out container of the whole page.
# "children =[]" is needed when more than 1 html element is present within the container.
layout = html.Div(
    children=[
        html.Div(
            id="Main-panel",
            children=[
                html.Div(html.H1("Log anomaly dashboard"), id="TitleDIV"),
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
                        # The three boxes on the page are currently hardcoded with values. These should of course
                        # be updated with the correct data going forward. Should be pretty easily done
                        # via dcc callbacks.
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.H3(
                                            "Anomalies", style={"margin-left": "20px"}
                                        ),
                                        html.H1(
                                            len(lst1), style={"margin-left": "20px"}
                                        ),
                                        html.H2("00%", style={"margin-left": "20px"}),
                                    ],
                                    style={
                                        "margin": "15px",
                                        "background-color": "#e0e0d1",
                                        "height": "30vh",
                                        "width": "25%",
                                        "outline-color": "#b7b795",
                                        "outline-style": "solid",
                                        "outline-width": "3px",
                                    },
                                ),
                                html.Div(
                                    children=[
                                        html.H3("Logs", style={"margin-left": "20px"}),
                                        html.H1("0", style={"margin-left": "20px"}),
                                        html.H2("00%", style={"margin-left": "20px"}),
                                    ],
                                    style={
                                        "margin": "15px",
                                        "background-color": "#e0e0d1",
                                        "height": "30vh",
                                        "width": "25%",
                                        "outline-color": "#b7b795",
                                        "outline-style": "solid",
                                        "outline-width": "3px",
                                    },
                                ),
                                html.Div(
                                    children=[
                                        html.H5(
                                            "Anomaly Inbox",
                                            style={"margin-left": "20px"},
                                        ),
                                        dash_table.DataTable(
                                            testDf.to_dict("records"),
                                            id="InboxTable",
                                            columns=[
                                                {"name": i, "id": i}
                                                for i in testDf.columns
                                            ],
                                            editable=True,
                                            sort_action="native",
                                            sort_mode="multi",
                                            style_table={
                                                "overflow": "auto",
                                                "height": "30vh",
                                                "marginBottom": "20px",
                                            },
                                            style_header={
                                                "backgroundColor": "#b3b3b3",
                                                "fontWeight": "bold",
                                            },
                                        ),
                                    ],
                                    style={
                                        "margin": "15px",
                                        "background-color": "#e0e0d1",
                                        "height": "8%",
                                        "width": "40%",
                                        "outline-color": "#b7b795",
                                        "outline-style": "solid",
                                        "outline-width": "3px",
                                    },
                                ),
                            ],
                            style={"display": "flex", "justify-content": "center"},
                            className="row",
                        ),
                    ]
                ),
                html.Div(
                    html.Div(
                        children=[
                            # Both graphs on the page are set here. Dash has the dcc.Graph component which takes
                            # a plotly figure as it's figure parameter. The style of it only defines
                            # the container containing the figure. All customization of the actual graph is done
                            # when defining the actual plotly figures.
                            dcc.Graph(
                                figure=ScatterPlotFig,
                                style={"width": "50vw", "height": "30vw"},
                            ),
                            dcc.Graph(
                                figure=PieChartFig,
                                style={"width": "30vw", "height": "30vw"},
                            ),
                        ],
                        style={"display": "flex", "justify-content": "center"},
                        className="row",
                    ),
                )
                # Style customization for the whole page container:
            ],
            style={"width": "85vw", "margin-left": "20px"},
        )
    ],
    style={"display": "flex", "width": "80vw"},
)


# Callbacks define the functionality of the dashboard.
@callback(
    Output("output-container-date-picker-range", "children"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
)
def update_output(start_date, end_date):
    string_prefix = "You have selected: "
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime("%B %d, %Y")
        string_prefix = string_prefix + "Start Date: " + start_date_string + " | "
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime("%B %d, %Y")
        string_prefix = string_prefix + "End Date: " + end_date_string
    if len(string_prefix) == len("You have selected: "):
        return "Select a date to see it displayed here"
    else:
        return string_prefix
