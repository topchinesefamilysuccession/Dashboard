import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
# import base64

import os

from app import app 
from apps import backtesting, allocations, market, strategies, sentiment, macro, landing

# image_filename = 'img/logo2_circle.png' # replace with your own image
# encoded_image = base64.b64encode(open(image_filename, 'rb').read())


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    
    html.Header([
        # html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), 
        #         style={'width':'70px','border-radius':'35px'}),
        dcc.Loading(dcc.Store(id='store'),type="cube", fullscreen=True), 
        html.H2("Top Chinese Strategies", className="logo"),
        html.Nav([
        html.Ul([
        #     html.Li([dcc.Link('Backtesting', href='/apps/backtesting', id="backtesting-header")]),
        #     html.Li([dcc.Link('Sentiment', href='/apps/sentiment', id="sentiment-header")]),
        #     html.Li([dcc.Link('Market Research', href='/apps/market', id="marketresearch-header")]),
        #     html.Li([dcc.Link('Macro Data', href='/apps/macro', id="macro-header")]),
            html.Li([dcc.Link('Landing Page', href='/apps/landing', id="landing-header")])
        ],className="nav_links")
    ]),
    
        html.Button("Build a Strategy", id="build-strat-btn"),
        
    ]),
    dcc.Checklist(id="language", options=[{"label":"Mandarin/中文", "value":"cn"}],inputStyle={"margin-right": "9px"}
),
    html.Div(id="page-content")
])

# @app.callback(
#      [Output("backtesting-header", "children"), Output("sentiment-header", "children"), Output("marketresearch-header", "children"),Output("macro-header", "children")],

#     [Input("language", "value")]
# )
# def translate_labels(language):
#     if language == ["cn"]:
#         language = "cn"
#     else:
#         language = "en"
        
#     if language == "cn":
#         backtesting_label = "回溯测试"
#         sentiment_label = "舆情"
#         market_label =  "市场调查"
#         macro_label =  "宏数据"
#     elif language == "en":
#         backtesting_label = "Backtesting"
#         sentiment_label = "Sentiment"
#         market_label =  "Market Research"
#         macro_label =  "Macro Data"
#         landing_label = "Landing Page"
    
#     return backtesting_label, sentiment_label, market_label,macro_label, landing_label



# @app.callback(
#     [Output("url", "pathname")],
#     [Input("build-strat-btn", "n_clicks")]
# )

# def build_strategy_page(v):
#     if v == None:
#         raise PreventUpdate
#     return ["/apps/strategies"]


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")], 
    State("store", "data")
)

def display_page(pathname, data):
    if pathname == "/apps/backtesting":
        return backtesting.layout
    elif pathname == "/apps/allocations":
        return allocations.layout
    elif pathname == "/apps/sentiment":
        return sentiment.layout
    elif pathname == "/apps/market":
        return market.layout
    elif pathname == "/apps/macro":
        return macro.layout
    elif pathname == "/apps/strategies":
        return strategies.load_strategy(data)
    elif pathname == "/apps/landing":
        return landing.layout
    else:
        return landing.layout



server = app.server

if __name__ == "__main__":
    # app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT',8080)))
    app.run_server(debug=True,port=int(os.environ.get('PORT',8080)))