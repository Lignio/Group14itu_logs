from turtle import st
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import dash
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import random
from plotly.graph_objs import *
from .testdata import genLists


dash.register_page(__name__)

#Not an actual page yet. Just for showing that pages can be changed.
testDf = pd.read_csv('Dashboard_with_pages\TestCSVLg.csv',delimiter=';')


layout = html.Div(children=[
    html.Div(
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

        html.Div(children=[
            #The datepicker is taken from the DCC page, and it's functionality is defined
            #in the callback in the bottom. 
            dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=date(1995, 8, 5),
            max_date_allowed=date(2017, 9, 19),
            initial_visible_month=date(2017, 8, 5),
            end_date=date(2017, 8, 25),
            ),
            html.Div(id='output-container-date-picker-range',style={})
        ]),

        html.Div(children=[
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
                            dbc.Input(id="input", className="bi bi-search fa-2x cardLine", placeholder="Search for an anomaly...", type="text",
                                    style={"width":"25vw","float":"right","background":"#f8f8f8"})
                        ,
                        
                    ], style={"margin":"10px 10px 10px 10px"}),
                    
                    dash_table.DataTable(
                        testDf.to_dict('records'),
                        id="InboxTable",
                        columns=[{"name": i, "id": i} for i in testDf.columns],
                        editable=True,
                        sort_action="native",
                        sort_mode='multi',
                        style_table={
                        'overflow' : 'auto',
                        'padding' : '20px 20px 20px 20px',
                        'marginBottom' : '20px'
                        },
                        style_header={
                        'background' : '#f8f8f8',
                        "color" : "black",
                        'fontWeight': 'bold'
                        })
                    ],
                    className="card bg-white DropShadow",
                    style={"margin":"15px","height":"8%","width":"70vw","display" : "flex", "justify-content" : "center"}
                )

],style={"padding-left":"30px","padding-top":"20px","background-color":"#f0f3f6","width":"80vw"})