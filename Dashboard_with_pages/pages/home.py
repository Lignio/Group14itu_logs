import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div(children=[
    html.H1("Welcome to the anomaly dashboard!", style={"margin-left": "20px"}),
    html.H3("Explore the pages on the lefthand side.", style={"margin-left": "20px"})
])