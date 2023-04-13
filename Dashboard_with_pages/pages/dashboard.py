from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import dash
import plotly.express as px
from datetime import date
import dash_bootstrap_components as dbc
import random
import requests
from plotly.graph_objs import *
from .testdata import genLists

#Separate pages need to be registered like this to show up in the page container in app.py
dash.register_page(__name__, path='/')


#jsonLst = requests.get("http://localhost:8002/getAnomalyList", params = {"threshold":0.02})
#dataList = jsonLst.json()
dataList = [["A",1],["B",2],["C",3]]
anomalyScoreList = []

for i in dataList: 
    anomalyScoreList.append(i[1])

anomalyToPiechart = [0,0,0]

def countvalues():
    for i in anomalyScoreList:
        if i < 0.024:
            anomalyToPiechart[0]+=1
        elif i > 0.024 and i < 0.026:
            anomalyToPiechart[1]+=1
        else:
            anomalyToPiechart[2]+=1
    print(anomalyToPiechart)
    return anomalyToPiechart

lst1, lst2 = genLists()
    

#The figures are currently just populated with test data. The figures are created
#with the plotly package, so all documentation is via plotly.
ScatterPlotFig = px.scatter(x=lst1,y=lst2,title="").update_layout(xaxis_title="Name length",yaxis_title="Name count",margin=dict(l=20, r=20, t=30, b=20))
PieChartFig = px.pie(values=countvalues(), names=["0.02 - 0.024", "0.024 - 0.026", ">0.026"], title="").update_layout(margin=dict(l=20, r=20, t=30, b=20))

testDf = pd.read_csv('Dashboard_with_pages\TestCSVLg.csv',delimiter=';')

#Layout = html.Div defines the out container of the whole page. 
#"children =[]" is needed when more than 1 html element is present within the container.
layout = html.Div(children=[ 

    html.Div(id="Main-panel",children=[       

        html.Div(
            html.H1("Anomaly Dashboard", className="FontBold"),
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
                    html.Li("Dashboard", className="breadcrumb-item active FontBold", style={"color":"black"})
                ])
            )
        ),

        html.Div(children=[
            dbc.DropdownMenu(
                label=" Today", 
                toggle_style={"background":"white", "color":"black"}, 
                toggleClassName="border-white DropShadow bi bi-calendar-day",
                direction="down",
                children=[
                dbc.DropdownMenuItem("All time", id="all_time_option"),
                dbc.DropdownMenuItem("Today", id="today_option"),
                dbc.DropdownMenuItem("Yesterday", id="yesterday_option" ),
                dbc.DropdownMenuItem("Last two days", id="last_two_days_option"),
                dbc.DropdownMenuItem("Last 7 days", id="last_7_days_option"),
                dbc.DropdownMenuItem("This month", id="this_month_option")

            ], className="", id="dropdownmenu",style={"margin-bottom":"20px"}),
        ]),
        html.Div(children=[
            #The three boxes on the page are currently hardcoded with values. These should of course
            #be updated with the correct data going forward. Should be pretty easily done
            #via dcc callbacks.
            html.Div(children=[
                html.Div(children=[
                    html.Div(children=[
                        html.I(className="bi bi-exclamation-circle fa-2x cardText cardLine FontBold IconBold", style={"float":"left"}),
                        html.I(className="bi bi-three-dots-vertical fa-2x cardText cardLine FontBold", style={"float":"right"})]
                    ),
                        html.H3("Anomalies", className="cardText card-title cardLine FontBold", style={"font-size":"20px"}),
                    html.Div(style={"padding-top":"7px"}, children=[
                        html.H1(len(lst1), className="cardText card-subtitle cardLine FontBold", style={"float":"left","padding-top":"12px","font-size":"45px", "color":"#1c1952"}),
                        html.Div(children=[
                            html.H2(" 00%", className="GreenCard bi bi-graph-up cardText card-subtitle cardLine FontBold IconBold", style={"float":"right","margin-top":"35px", "font-size":"20px", "padding":"5px 10px 5px"})
                        ]),
                        
                    ])],        
                    style={"margin":"5px","background-color":"#ffffff","height":"37vh","width":"24%","border":"none", "margin-right":"15px"},
                    className="card rounded DropShadow"
                ),
                html.Div(children=[
                    html.Div(children=[
                        html.I(className="bi bi-exclamation-triangle fa-2x cardText cardLine FontBold IconBold", style={"float":"left"}),
                        html.I(className="bi bi-three-dots-vertical fa-2x cardText cardLine FontBold", style={"float":"right"})]
                    ),
                        html.H3("False-Positives", className="cardText card-title cardLine FontBold", style={"font-size":"20px"}),
                    html.Div(style={"padding-top":"7px"}, children=[
                        html.H1(len(lst1), className="cardText card-subtitle cardLine FontBold", style={"float":"left","padding-top":"12px","font-size":"45px", "color":"#1c1952"}),
                        html.Div(children=[
                            html.H2(" 00%", className="RedCard bi bi-graph-up cardText card-subtitle cardLine FontBold IconBold", style={"float":"right","margin-top":"35px", "font-size":"20px", "padding":"5px 10px 5px"})
                        ]),

                    ])],        
                    style={"margin":"5px","background-color":"#ffffff","height":"37vh","width":"24%","border":"none","margin-right":"37px"},
                    className="card DropShadow"
                ),
                html.Div(children=[
                    html.Div(children=[
                    html.H5("Anomaly Inbox", className="cardText cardLine card-title FontBold",style={"margin-top": "10px", "float":"left"}),
                    html.I(className="bi bi-exclamation-circle fa-1x cardLine", style={"float":"right","margin-right":"5px","margin-top":"3px", "font-size":"25px"})]),
                    dash_table.DataTable(
                        testDf.to_dict('records'),
                        id="InboxTable",
                        columns=[{"name": i, "id": i} for i in testDf.columns],
                        editable=True,
                        sort_action="native",
                        sort_mode='multi',
                        style_table={
                        'overflow': 'auto',
                        'height' : '37vh',
                        'marginBottom' : '20px'
                        },
                        style_header={
                        'background': '#141446',
                        'color' : 'white',
                        'fontWeight': 'bold'
                        })
                    ],
                    style={"margin":"5px","background-color":"#e0e0d1","height":"50vh","width":"40%","border":"none","margin-top":"-65px"},
                     className="card bg-white rounded DropShadow"
                ),
            
            ],style={"display": "flex","margin-left":"-5px"},className="row"),
        ]),

        html.Div(

            html.Div(children=[

                #Both graphs on the page are set here. Dash has the dcc.Graph component which takes
                #a plotly figure as it's figure parameter. The style of it only defines
                #the container containing the figure. All customization of the actual graph is done
                #when defining the actual plotly figures.
                html.Div(children=[
                    html.H5("Anomalies Over Time", className="cardText card-title FontBold", style={"margin-left":"10px", "margin-top":"10px"}),
                    dcc.Graph(
                    
                    figure=ScatterPlotFig, className="",
                    style={"width":"40vw","height":"20vw","padding":"10px 10px 10px 10px"}
                )
                ], className="card border-0 DropShadow", style={"margin-right":"35px"})
                ,
                html.Div(children=[
                    html.H5("Severity Percentage", className="cardText card-title FontBold", style={"margin-left":"10px", "margin-top":"10px"}),
                    dcc.Graph(
                    figure = PieChartFig, className="",
                    style={"width" : "32vw","height" : "20vw", "padding":"10px 10px 10px 10px"}
                )
                ], className="card border-0 DropShadow")
                

            ],style={"display": "flex"  ,"padding-top":"30px","padding-bottom":"20px"}),
        )

        #Style customization for the whole page container:
],style={"width" : "85vw", "margin-left":"30px"})], style={"display":"flex","width" : "80vw", "background-color":"#f0f3f6","padding-top":"20px"})


#Callbacks define the functionality of the dashboard.
@callback(
    Output('output-container-date-picker-range', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix

@callback(
    Output("dropdownmenu", "label"),
    [Input("all_time_option", "n_clicks"), Input("today_option", "n_clicks"),
     Input("yesterday_option", "n_clicks"), Input("last_two_days_option", "n_clicks"),
     Input("last_7_days_option", "n_clicks"), Input("this_month_option", "n_clicks")])
def update_dropdownmenu_label(n1,n2,n3,n4,n5,n6):
    #Maps the ids of the dropdown menu to their text
    #and changes the label of the dropdownmenu.
    id_lookup = {"all_time_option":" All time", 
                 "today_option":" Today",
                 "yesterday_option":" Yesterday",
                 "last_two_days_option":" Last Two Days",
                 "last_7_days_option":" Last 7 Days",
                 "this_month_option":" This month"}
    
    ctx = dash.callback_context

    #This gets the id of the button that triggered the callback
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return id_lookup[button_id]