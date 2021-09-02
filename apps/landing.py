from logging import PercentStyle
import dash_core_components as dcc
from dash_core_components.Loading import Loading
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_html_components.Div import Div
from numpy.lib.arraypad import _as_pairs
from .base.fred_utils import FredHandler
from .base.charts_utils import Chart, init_chart
from .base.api_handler import StrategiesAPI
from .base.trend_utils import TrendsMaster
import dash_table
from dash import no_update
from .base.general_utils import get_all_xtb_assets, get_ETF_from_component
import pandas as pd
from app import app
from datetime import datetime

df = get_all_xtb_assets()
tm = TrendsMaster()

def getTickerTreeMap():
    ticker_treemap_data = tm.getTickerTrends()
    ticker_treemap = Chart('Trend Chart')
    ticker_treemap.getTrendMap(ticker_treemap_data)
    return ticker_treemap.get_chart()

def getTagTreeMap():
    tag_treemap_data = tm.getTagTrends()
    tag_treemap = Chart('Trend Chart')
    tag_treemap.getTrendMap(tag_treemap_data)
    return tag_treemap.get_chart()

tickerTreeMap = getTickerTreeMap()
tagTreeMap = getTagTreeMap()

list_of_assets = df["keywords"].unique()

layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='landing-selection',

            options=[
                {"label":asset, "value":asset} for asset in list_of_assets
            ],
            multi=True
            ), 

        html.Div([
            dcc.Checklist(
                id="suggestions-toggle",
                options=[
                    {"label":"Show Suggestions", "value":"suggestions"}
                ]
            ),
            html.Button("Go", id="go-btn")
        ], className="landing-controls-div"),

        html.Div([
            dcc.Dropdown(
                id='suggestions',

                options=[

                    {"label":asset, "value":asset} for asset in list_of_assets
                ],
                multi=True,
                value=list_of_assets), 

        ], className="suggestions-div", id="suggestions-id"),
        
    ], className='search-bar'),

    html.Div([
        html.Div([
            html.H3('Daily Top Trends'),
            html.P(datetime.today().date().strftime("%d %B %Y"))
        ], className='trends-title'),
        dcc.Loading(children=[
            html.Div([
                html.Div([
                    dcc.Graph(figure=tickerTreeMap,
                                config={
                                    'displayModeBar':False
                                },
                                clear_on_unhover = True,
                    id='ticker_graph'),
                ], className='ticker-trend'),
                html.Div([
                    dcc.Graph(figure=tagTreeMap,
                                config={
                                    'displayModeBar':False
                                },
                                clear_on_unhover=True,
                    id='tag_graph'),
                ], className='tag-trend'),
            ], className='trend-graphs-container')
        ])
    ], className='sentiment-trends')
            
        
], className="landing-content")

@app.callback(
    [
        Output("landing-selection", "value"), 
        Output("suggestions", "options"), 
        Output("suggestions", "value")
    ],
    [Input("suggestions", "value"), Input("landing-selection", "value"),Input('ticker_graph','clickData')], 
    [State("landing-selection", "options"), State("suggestions", "options")]
)
def update_list(suggestion_values, selected_value, ticker_clickData,
                landing_options, suggestions_options):

    if selected_value is None:
        selected_value = []
    
    if ticker_clickData is not None:
        # print(ticker_clickData)
        # print(ticker_clickData['points'][0]['text'])
        etfs = get_ETF_from_component(ticker_clickData['points'][0]['text'])
        # print(f'ETFs that matched the componenet: {etfs}')
        selected_value = list(df[df.symbol.isin(etfs)]['keywords'])

    #Which values were selected ?
    keywords_full_list = [list(d.values())[0] for d in suggestions_options]
    suggestion_values_selected = [v for v in keywords_full_list if v not in suggestion_values]
    

    #Suggestions and already selected values
    updated_selected_values = list(set(selected_value + suggestion_values_selected))

    #Update suggestion values and options
    all_keywords = [list(d.values())[0] for d in landing_options]
    updated_suggestion_values = [v for v in all_keywords if v not in updated_selected_values]
    suggested_options = [{"label": v, "value":v} for v in updated_suggestion_values]

    return updated_selected_values, \
            suggested_options, \
            updated_suggestion_values

@app.callback(
    Output("suggestions-id", "style"), 
    [Input("suggestions-toggle", "value")]
)

def show_hide_suggestions(toggle_value):
    if toggle_value is None or toggle_value == []:
        return {"display":"none"}
    return {"display":"flex"}

# @app.callback(
#     Output('ticker_graph','figure'),
#     [Input('ticker_graph','hoverData')]
# )

# def trendHoverkHandle(hoverData):
#     # print(hoverData)
#     for shape in tickerTreeMap['layout']['shapes']:
#         shape['line']['color'] = '#ffffff'
#     if hoverData:
#         tickerTreeMap['layout']['shapes'][hoverData['points'][0]['pointIndex']]['line']['color'] = '#000000' 
#     return tickerTreeMap


@app.callback(
    [Output("url", "pathname"), Output("store", "data")],
    [Input("go-btn", "n_clicks")], 
    [State("landing-selection", "value")]
)

def redirect_page(v, selected_assests):

    if not selected_assests is None:
        selected_assets_translated = df[df["keywords"].isin(selected_assests)]["symbol"].values.tolist()
        strategy_api = StrategiesAPI()
        r = strategy_api.run_strategy("S1", selected_assests)
        return "/apps/strategies", r
    if v == None:
        raise PreventUpdate
    return ["/apps/strategies"] 



# landing-content

# @app.callback(
#     [Output("landing-content", "children"), Output("store", "data")],
#     [Input("go-btn", "n_clicks")], 
#     [State("landing-selection", "value")]
# )

# def redirect_page(v, selected_assests):

#     if not selected_assests is None:
#         selected_assets_translated = df[df["keywords"].isin(selected_assests)]["symbol"].values.tolist()
#         strategy_api = StrategiesAPI()
#         r = strategy_api.run_strategy("S1", selected_assests)
#         return "/apps/strategies", r
#     if v == None:
#         raise PreventUpdate
#     return ["/apps/strategies"] 