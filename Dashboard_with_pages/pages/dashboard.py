from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import dash
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import requests
from plotly.graph_objs import *
import json
import time
from pydantic import BaseSettings


class Settings(BaseSettings):
    controller: str


settings = Settings()

controller = settings.controller

get_anomaly_list = f"{controller}/get_anomaly_list"
# Separate pages need to be registered like this to show up in the page container in app.py
dash.register_page(__name__, path="/")


# Gets the dataframe but without the extra colum of buttons
def getDataDFSlim():
    data = requests.get(get_anomaly_list).json()
    jsonData = json.dumps(data)
    actualDataDF = pd.read_json(jsonData, convert_dates=False)
    actualDataDF = actualDataDF.reindex(
        columns=["id", "log_message", "log_time", "false_positive", "anomaly_score"]
    )
    return actualDataDF


# Gets the dataframe but reduced to only contain id, log_message and anomaly_score
def getDataDFInbox():
    data = getDataDFSlim()
    dataFrame = data.reindex(columns=["id", "log_message", "anomaly_score"])
    dataFrame = dataFrame.rename(columns={"anomaly_score": "a_score"})
    return dataFrame


# Creates and returns a list of all anomaly_scores in the dataframe
def getAnomalyScoreList():
    anomalyScoreList = []
    for i in getDataDFSlim().anomaly_score:
        anomalyScoreList.append(i)
    return anomalyScoreList


# returns a dictionary with each date an anomaly has appeared
# and the amount of anomalies for each date
# Used for wave graph
def getAnomalyByDate():
    anomalyDateList = {}

    helperMap = {}

    for i in getDataDFSlim().log_time:
        if i in helperMap:
            helperMap[i] = helperMap[i] + 1
        else:
            helperMap[i] = 1

    anomalyDateList["Date"] = helperMap.keys()
    anomalyDateList["Amount"] = helperMap.values()

    return anomalyDateList


# def getAnomaliesInPeriode():


# Creates and returns a list of all false positives
def getListOfFalsePostives():
    data = []
    for i in getDataDFSlim().false_positive:
        if i == True:
            data.append(i)
    return data


def procentOfFalsePositives():
    return round(((len(getListOfFalsePostives())) / (len(getDataDFSlim()))) * 100, 2)


# Counts and partitions the anomaly scores in the anomalyScore list into a list used for the piechart
def countvalues():
    anomalyToPiechart = [0, 0, 0]
    anomalyScoreList = getAnomalyScoreList()
    for i in anomalyScoreList:
        if i < 0.024:
            anomalyToPiechart[0] += 1
        elif i > 0.024 and i < 0.026:
            anomalyToPiechart[1] += 1
        else:
            anomalyToPiechart[2] += 1
    return anomalyToPiechart


# Entire html is now moved into a serve_layout() method which allows for reloading data when refreshing the page
def serve_layout():
    # lists used for creating graphs
    lst1 = getDataDFSlim().id
    lst2 = getListOfFalsePostives()

    # used for making the inbox table
    inboxDataFrame = getDataDFInbox()
    PieChartFig = px.pie(
        values=countvalues(),
        names=["0.02 - 0.024", "0.024 - 0.026", ">0.026"],
        title="",  # Title is blank
    ).update_layout(margin=dict(l=20, r=20, t=30, b=20))

    # used for making the line graph, gets its values from getAnomalyByDate()
    waveChartFig = px.line(getAnomalyByDate(), x="Date", y="Amount").update_layout(
        margin=dict(l=20, r=20, t=30, b=20)
    )

    return html.Div(
        children=[
            html.Div(
                id="Main-panel",
                children=[
                    dcc.Interval(id="count_update_interval", interval=1 * 1000),
                    html.Div(
                        # Dashboard title
                        html.H1("Anomaly Dashboard", className="FontBold"),
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
                                        "Dashboard",
                                        className="breadcrumb-item active FontBold",
                                        style={"color": "black"},
                                    ),
                                ],
                            )
                        )
                    ),
                    # Dropdown menu - each of the items have been given an id. This is used for callback.
                    # Label is the text being shown on the Dropdown Menu
                    # ClassName/Style doesn't work. Instead toggle_style/toggleClassName is used.
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
                                className="border-white DropShadow",
                                id="interval_selector",
                                style={
                                    "width": "10vw",
                                    "margin-bottom": "20px",
                                    "background": "white",
                                    "color": "black",
                                },
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            # The three boxes on the page are currently hardcoded with values. These should of course
                            # be updated with the correct data going forward. Should be pretty easily done
                            # via dcc callbacks.
                            html.Div(
                                children=[
                                    # Anomalies box, shows number of anomalies.
                                    html.Div(
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.I(
                                                        className="bi bi-exclamation-circle fa-2x cardText cardLine FontBold IconBold",
                                                        style={"float": "left"},
                                                    ),
                                                    # This is the three vertical dots. It is commented out since it has no functionality.
                                                    # It should not be deleted!
                                                    # html.I(className="bi bi-three-dots-vertical fa-2x cardText cardLine FontBold", style={"float":"right"})
                                                ]
                                            ),
                                            html.H3(
                                                "Anomalies",
                                                className="cardText card-title cardLine FontBold",
                                                style={"font-size": "20px"},
                                            ),
                                            html.Div(
                                                style={"padding-top": "7px"},
                                                children=[
                                                    html.H1(
                                                        len(lst1),
                                                        id="anomaly_count",
                                                        className="cardText card-subtitle cardLine FontBold",
                                                        style={
                                                            "float": "left",
                                                            "padding-top": "12px",
                                                            "font-size": "45px",
                                                            "color": "#1c1952",
                                                        },
                                                    ),
                                                    html.Div(
                                                        children=[
                                                            html.H2(
                                                                " 00%",
                                                                className="GreenCard bi bi-graph-up cardText card-subtitle cardLine FontBold IconBold",
                                                                style={
                                                                    "float": "right",
                                                                    "margin-top": "35px",
                                                                    "font-size": "20px",
                                                                    "padding": "5px 10px 5px",
                                                                },
                                                            )
                                                        ]
                                                    ),
                                                ],
                                            ),
                                        ],
                                        style={
                                            "margin": "5px",
                                            "background-color": "#ffffff",
                                            "height": "37vh",
                                            "width": "24%",
                                            "border": "none",
                                            "margin-right": "15px",
                                        },
                                        className="card rounded DropShadow",
                                    ),
                                    # False-Positives box, shows number of False-Positives.
                                    html.Div(
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.I(
                                                        className="bi bi-exclamation-triangle fa-2x cardText cardLine FontBold IconBold",
                                                        style={"float": "left"},
                                                    ),
                                                    # This is the three vertical dots. It is commented out since it has no functionality.
                                                    # It should not be deleted!
                                                    # html.I(className="bi bi-three-dots-vertical fa-2x cardText cardLine FontBold", style={"float":"right"})
                                                ]
                                            ),
                                            html.H3(
                                                "False-Positives",
                                                className="cardText card-title cardLine FontBold",
                                                style={"font-size": "20px"},
                                            ),
                                            html.Div(
                                                style={"padding-top": "7px"},
                                                children=[
                                                    html.H1(
                                                        len(lst2),
                                                        id="false_positive_count",
                                                        className="cardText card-subtitle cardLine FontBold",
                                                        style={
                                                            "float": "left",
                                                            "padding-top": "12px",
                                                            "font-size": "45px",
                                                            "color": "#1c1952",
                                                        },
                                                    ),
                                                    html.Div(
                                                        children=[
                                                            html.H2(
                                                                str(
                                                                    procentOfFalsePositives()
                                                                )
                                                                + "%",
                                                                className="GreenCard bi bi-graph-up cardText card-subtitle cardLine FontBold IconBold",
                                                                style={
                                                                    "float": "right",
                                                                    "margin-top": "35px",
                                                                    "font-size": "20px",
                                                                    "padding": "5px 10px 5px",
                                                                },
                                                            )
                                                        ]
                                                    ),
                                                ],
                                            ),
                                        ],
                                        style={
                                            "margin": "5px",
                                            "background-color": "#ffffff",
                                            "height": "37vh",
                                            "width": "24%",
                                            "border": "none",
                                            "margin-right": "37px",
                                        },
                                        className="card DropShadow",
                                    ),
                                    # Anomaly Inbox - It is made using a DataTable.
                                    html.Div(
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.H5(
                                                        "Anomaly Inbox",
                                                        className="cardText cardLine card-title FontBold",
                                                        style={
                                                            "margin-top": "10px",
                                                            "float": "left",
                                                        },
                                                    ),
                                                    html.I(
                                                        className="bi bi-exclamation-circle fa-1x cardLine",
                                                        style={
                                                            "float": "right",
                                                            "margin-right": "5px",
                                                            "margin-top": "3px",
                                                            "font-size": "25px",
                                                        },
                                                    ),
                                                ]
                                            ),
                                            dash_table.DataTable(
                                                id="InboxTable",
                                                columns=[
                                                    {
                                                        "name": i,
                                                        "id": i,
                                                        "type": "numeric",
                                                    }
                                                    # This allows us to limit decimals in anomaly_score (a_score)
                                                    if i != "a_score"
                                                    else {
                                                        "name": i,
                                                        "id": i,
                                                        "type": "numeric",
                                                        "format": {"specifier": ".4f"},
                                                    }
                                                    for i in inboxDataFrame.columns
                                                ],
                                                data=inboxDataFrame.to_dict("records"),
                                                editable=False,
                                                sort_action="native",
                                                sort_mode="multi",
                                                style_table={
                                                    "overflow": "auto",
                                                    "height": "37vh",
                                                    "marginBottom": "20px",
                                                },
                                                style_header={
                                                    "background": "#141446",
                                                    "color": "white",
                                                    "fontWeight": "bold",
                                                },
                                                style_data={
                                                    "whiteSpace": "normal",
                                                    "width": "60px",
                                                },
                                                # Also used to limit decimals in anomaly_score (a_score)
                                                style_data_conditional=[
                                                    {
                                                        "if": {"column_id": "a_score"},
                                                        "format": {"specifier": ".4f"},
                                                    }
                                                ],
                                            ),
                                        ],
                                        # This is styling for the Anomaly Inbox
                                        style={
                                            "margin": "5px",
                                            "background-color": "#e0e0d1",
                                            "height": "50vh",
                                            "width": "40%",
                                            "border": "none",
                                            "margin-top": "-65px",
                                        },
                                        className="card bg-white rounded DropShadow",
                                    ),
                                ],
                                style={"display": "flex", "margin-left": "-5px"},
                                className="row",
                            ),
                        ]
                    ),
                    html.Div(
                        html.Div(
                            children=[
                                dcc.Interval(
                                    id="graph_update_interval",
                                    interval=5 * 1000,
                                    n_intervals=0,
                                ),
                                # Both graphs on the page are set here. Dash has the dcc.Graph component which takes
                                # a plotly figure as it's figure parameter. The style of it only defines
                                # the container containing the figure. All customization of the actual graph is done
                                # when defining the actual plotly figures.
                                html.Div(
                                    children=[
                                        html.H5(
                                            "Anomalies Over Time",
                                            className="cardText card-title FontBold",
                                            style={
                                                "margin-left": "10px",
                                                "margin-top": "10px",
                                            },
                                        ),
                                        dcc.Graph(
                                            id="waveGraph",
                                            figure=waveChartFig,
                                            className="",
                                            style={
                                                "width": "40vw",
                                                "height": "20vw",
                                                "padding": "10px 10px 10px 10px",
                                            },
                                        ),
                                    ],
                                    className="card border-0 DropShadow",
                                    style={"margin-right": "35px"},
                                ),
                                html.Div(
                                    children=[
                                        html.H5(
                                            "Severity Percentage",
                                            className="cardText card-title FontBold",
                                            style={
                                                "margin-left": "10px",
                                                "margin-top": "10px",
                                            },
                                        ),
                                        dcc.Graph(
                                            id="piechart",
                                            figure=PieChartFig,
                                            className="",
                                            style={
                                                "width": "32vw",
                                                "height": "20vw",
                                                "padding": "10px 10px 10px 10px",
                                            },
                                        ),
                                    ],
                                    className="card border-0 DropShadow",
                                ),
                            ],
                            style={
                                "display": "flex",
                                "padding-top": "30px",
                                "padding-bottom": "20px",
                            },
                        ),
                    )
                    # Style customization for the whole page container:
                ],
                style={"width": "85vw", "margin-left": "30px"},
            )
        ],
        style={
            "display": "flex",
            "width": "80vw",
            "background-color": "#f0f3f6",
            "padding-top": "20px",
        },
    )


# Sets the layout to our serve_layout
layout = serve_layout


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
    [
        Input("interval_selector", "value"),
        Input("count_update_interval", "n_intervals"),
    ],
)
def adjust_table(value, interval):
    time.sleep(0.1)
    actualDataDF = getDataDFSlim()
    interval = calculate_interval(value)

    copyDf = actualDataDF[
        (actualDataDF["log_time"] <= interval[0])
        & (actualDataDF["log_time"] >= interval[1])
    ]
    return copyDf.to_dict(orient="records")


# Call backs for updating graphs
@callback(
    Output("waveGraph", component_property="figure"),
    Input("graph_update_interval", "n_intervals"),
)
def update_wavegraph(intervals):
    return px.line(getAnomalyByDate(), x="Date", y="Amount").update_layout(
        margin=dict(l=20, r=20, t=30, b=20)
    )


@callback(
    Output("piechart", component_property="figure"),
    Input("graph_update_interval", "n_intervals"),
)
def update_piechart(intervals):
    return px.pie(
        values=countvalues(),
        names=["0.02 - 0.024", "0.024 - 0.026", ">0.026"],
        title="",  # Title is blank
    ).update_layout(margin=dict(l=20, r=20, t=30, b=20))


@callback(
    Output("anomaly_count", "children"), Input("count_update_interval", "n_intervals")
)
def update_anomaly_count(interval):
    return len(getDataDFSlim().id)


@callback(
    Output("false_positive_count", "children"),
    Input("count_update_interval", "n_intervals"),
)
def update_false_positive_count(interval):
    return len(getListOfFalsePostives())
