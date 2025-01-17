from dash import Dash, dcc, html, Input, Output, State, ctx, callback
import dash
import dash_bootstrap_components as dbc
import requests
from pydantic import BaseSettings
import keyCloakHandler



class Settings(BaseSettings):
    controller: str


settings = Settings()

controller = settings.controller

check_flag = f"{controller}/check_flag"

##The app.py page does not actually contain the pages that are being loaded, it is more so a container
# for pages. It only contains the sidebar (containing buttons to navigate) and a page_container.
# The page container then loads the actual pages from the pages directory.
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    use_pages=True,
)
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            id="Sidebar",
            children=[
                dcc.Location(id="locApp"),
                dcc.Interval(id="interval-component", interval=1 * 5000, n_intervals=0),
                html.Div(
                    children=[
                        html.H2("SYSTEMATIC", className="FontLogo", id="Logo"),
                        ##The modal button is only for showing a pop up and the callback associated with a pop up.
                        # It should be deleted at some point.
                        html.Div(
                            html.H5(
                                "Anomaly Detector",
                                className="FontMain FontWhite SideElement",
                            )
                        ),
                    ]
                ),
                # Dashboard and anomaly button taken from a registry containing all of the pages
                html.Div(
                    children=[
                        html.Div(
                            html.Div(style={"display": "hidden"}, id="hiddendiv")
                            if "Login" in f" {page['name']}"
                            else dbc.Button(
                                f" {page['name']}",
                                color="secondary",
                                class_name="SideBTN SideElement bi bi-kanban",
                                href=page["relative_path"],
                            )
                            if "Dashboard" in f" {page['name']}"
                            else dbc.Button(
                                f" {page['name']}",
                                color="secondary",
                                class_name="SideBTN SideElement bi bi-exclamation-circle",
                                href=page["relative_path"],
                            ),
                            style={
                                "margin-top": "5vh",
                                "margin-left": "2%",
                                "font-weight": "500",
                            },
                        )
                        for page in dash.page_registry.values()  # load pages for the sidebar
                    ]
                ),
                # only login/logout button
                # outside the rest of the button to handle the change of name and function with login/logout
                html.Div(  #
                    children=[
                        html.Div(
                            html.Div(style={"display": "hidden"})
                            if "Dashboard"
                            in f" {dash.page_registry['pages.login']['name']}"  # Makes the pictogram different from dashboard
                            else dbc.Button(
                                "",
                                id="logInOutBtn",
                                n_clicks=0,
                                color="secondary",
                                class_name="SideBTN SideElement bi bi-exclamation-circle",
                                href=dash.page_registry["pages.login"]["relative_path"],
                            ),
                            style={
                                "margin-top": "5vh",
                                "margin-left": "2%",
                                "font-weight": "500",
                            },
                        )
                    ]
                ),
            ],
        ),
        html.Div(id="Main-panel", children=[dash.page_container]),
        dbc.Alert(
            [
                html.H4(
                    "New anomaly detected",
                    className="alert-heading",
                ),
                html.Div(
                    [
                        dbc.Button(
                            "Dismiss",
                            id="dismiss",
                            className=" alertBtn",
                            style={"float": "left"},
                        ),
                        dbc.Button(
                            "Go to anomalies",
                            id="goTo",
                            className="alertBtn",
                            n_clicks=0,
                            href="/anomalies",
                            style={"float": "right"},
                        ),
                    ],
                    id="alertBtnContainer",
                ),
            ],
            id="alertMsg",
            color="light",
            is_open=False,  # Not sure if this line should be here.
        ),
    ],
    style={"display": "flex", "width": "100vw"},
)


# Callback that toggles the alert of new anomalies.
@app.callback(
    Output("alertMsg", "is_open"),
    Input("interval-component", "n_intervals"),
    Input("goTo", "n_clicks"),
    Input("dismiss", "n_clicks"),
    State("alertMsg", "is_open"),
    prevent_initial_call=True,
)
def toggle_alert(n1, n2, n3, is_open):
    if (
        keyCloakHandler.CurrentUser is not None
        and keyCloakHandler.CurrentUser.isLoggedIn()
    ):
        triggered_id = ctx.triggered_id
        if triggered_id == "interval-component":
            return check_for_new_anomalies(is_open)
        else:
            return not is_open
    else:
        return False


def check_for_new_anomalies(is_open):
    isFlagged = requests.get(check_flag).json()  # Calls checkFlag in Controller
    if isFlagged:
        return True
    return is_open


# changes the button from login to logout depending on currentuser
@app.callback(Output("logInOutBtn", "children"), Input("logInOutBtn", "n_clicks"))
def changeLogIn(n_clicks):
    if keyCloakHandler.CurrentUser is None:
        return "Log in"
    elif keyCloakHandler.CurrentUser.isLoggedIn():
        return "Log out"
    return "Log in"


@callback(
    Output("locApp", "href"),
    Input("logInOutBtn", "n_clicks"),
    prevent_initial_call=True,
)
def logout(value):
    if value != 0:
        keyCloakHandler.CurrentUser.logout()
        return "http://127.0.0.1:8050/login"

