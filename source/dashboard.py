import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from backend import dt_continents, dt_countries, get_countries_by_continent, get_data_plot

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(
                        dbc.NavbarBrand("COVID-19 Dashboard", className="ml-2")
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://plot.ly",
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)

LEFT_COLUMN = dbc.Jumbotron(
    [
        html.H4(children="Dahsboard setup", className="display-5"),
        html.Hr(className="my-2"),

        html.Label("Select units", className="lead"),
        # html.P(
        #     "(Population data 2018)",
        #     style={"fontSize": 10, "font-weight": "lighter"},
        # ),
        dbc.RadioItems(
            id='radio-units',
            options=[
                {'label': "People", 'value': 'people'},
                {'label': "% Population", 'value': 'population', 'disabled': True},
            ],
            value='people',
        ),

        html.Label("Select dataset", style={"marginTop": 20}, className="lead"),
        dbc.RadioItems(
            id='radio-cases',
            options=[
                {'label': "Cases", 'value': 'totalCases'},
                {'label': "Deaths", 'value': 'totalDeaths'},
                {'label': "Recovered", 'value': 'recovered', 'disabled': True},
            ],
            value='totalCases',
        ),

        html.Label("Select countries", style={"marginTop": 20}, className="lead"),
        dcc.Dropdown(
            id="drop-continents",
            clearable=True,
            style={"marginBottom": 10, "font-size": 12},
            options=dt_continents,
            placeholder="Select continent",
            value='SA'
        ),
        dcc.Dropdown(
            id="drop-countries",
            clearable=True,
            multi=True,
            style={"marginBottom": 20, "font-size": 12},
            options=dt_countries,
            placeholder="Select countries",
            # value=['COL']
        ),
    ]
)

MIDDLE_COLUMN = [
    dbc.CardHeader(html.H5("Plot cases/deaths")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="loading-banks-hist",
                children=[
                    dbc.Alert(
                        "Not enough data to render this plot, please adjust the filters",
                        id="no-data-alert-bank",
                        color="warning",
                        style={"display": "none"},
                    ),
                    dcc.Graph(id="plot-dates"),
                    dcc.Graph(id="plot-days"),
                ],
                type="default",
            )
        ],
        style={"marginTop": 0, "marginBottom": 0},
    ),
]

RIGHT_COLUMN = [
    dbc.CardHeader(html.H5("Top countries")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Loading(
                            id="loading-dates",
                            children=[dcc.Graph(id="plot_dates")],
                            type="default",
                        )
                    ),
                ]
            )
        ]
    ),
]

BODY = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(LEFT_COLUMN, md=4),
                dbc.Col(dbc.Card(MIDDLE_COLUMN), md=8),
                # dbc.Col(dbc.Card(RIGHT_COLUMN), md=3),
            ],
            style={"marginTop": 30},
        ),
    ],
    className="mt-12",
)

# server = flask.Flask(__name__)
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(children=[NAVBAR, BODY])


@app.callback(
    Output('drop-countries', 'value'),
    [
        Input('drop-continents', 'value')
    ]
)
def update_countries(continent):
    return get_countries_by_continent(continent)


@app.callback(
    [
        Output('plot-dates', 'figure'),
        Output('plot-days', 'figure'),
    ],
    [
        Input('drop-countries', 'value'),
        Input('radio-cases', 'value'),
        Input('radio-units', 'value'),
    ],
)
def update_plots(countries, cases, units):
    return get_data_plot(countries, cases, units)


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port='8051', debug=True)
    pass
