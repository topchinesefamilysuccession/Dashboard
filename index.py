import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
# import base64

from app import app 
from apps import backtesting, allocations, models, strategies, sentiment


# image_filename = 'img/logo2_circle.png' # replace with your own image
# encoded_image = base64.b64encode(open(image_filename, 'rb').read())



app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    
    html.Header([
        # html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), 
        #         style={'width':'70px','border-radius':'35px'}),
        html.H2("Top Chinese Strategies", className="logo"),
        html.Nav([
        html.Ul([
            html.Li([dcc.Link('Backtesting', href='/apps/backtesting')]),
            html.Li([dcc.Link('Sentiment', href='/apps/sentiment')]),
            html.Li([dcc.Link('Models', href='/apps/models')]),
        ],className="nav_links")
    ]),
    
        html.Button("Build a Strategy", id="build-strat-btn"),
        
    ]),
    dcc.Checklist(id="language", options=[{"label":"Mandarin/中文", "value":"cn"}],inputStyle={"margin-right": "9px"}
),
    html.Div(id="page-content")
])


@app.callback(
    [Output("url", "pathname")],
    [Input("build-strat-btn", "n_clicks")]
)

def build_strategy_page(v):
    if v == None:
        raise PreventUpdate
    return ["/apps/strategies"]



@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)

def display_page(pathname):
    if pathname == "/apps/backtesting":
        return backtesting.layout
    elif pathname == "/apps/allocations":
        return allocations.layout
    elif pathname == "/apps/sentiment":
        return sentiment.layout
    elif pathname == "/apps/models":
        return models.layout
    elif pathname == "/apps/strategies":
        return strategies.layout
    else:
        return backtesting.layout

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)