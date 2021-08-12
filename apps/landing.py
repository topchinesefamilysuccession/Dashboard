import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_html_components.Div import Div
from .base.fred_utils import FredHandler
from .base.charts_utils import Chart, init_chart
from .base.api_handler import StrategiesAPI
from .base.trend_utils import TrendsMaster
import dash_table
from .base.general_utils import get_all_xtb_assets
import pandas as pd
from app import app
from datetime import datetime

df = get_all_xtb_assets()
tm = TrendsMaster()

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
        html.Div([
            html.Div([
                dcc.Graph(id='ticker-treemap'),
            ], className='ticker-trend'),
            html.Div([
                dcc.Graph(id='tag-treemap'),
            ], className='tag-trend'),
        ], className='trend-graphs-container'),
    ], className='sentiment-trends'),    
        
], className="landing-content")

@app.callback(
    [
        Output("landing-selection", "value"), 
        Output("suggestions", "options"), 
        Output("suggestions", "value"), 
        Output("ticker-treemap","figure"), 
        Output("tag-treemap","figure")
    ],
    [Input("suggestions", "value"), Input("landing-selection", "value")], 
    [State("landing-selection", "options"), State("suggestions", "options")]
)
def update_list(suggestion_values, selected_value, landing_options, suggestions_options):

    if selected_value is None:
        selected_value = []
        
    #Which values were selected ?
    keywords_full_list = [list(d.values())[0] for d in suggestions_options]
    suggestion_values_selected = [v for v in keywords_full_list if v not in suggestion_values]
    

    #Suggestions and already selected values
    updated_selected_values = list(set(selected_value + suggestion_values_selected))


    #Update suggestion values and options
    all_keywords = [list(d.values())[0] for d in landing_options]
    updated_suggestion_values = [v for v in all_keywords if v not in updated_selected_values]
    suggested_options = [{"label": v, "value":v} for v in updated_suggestion_values]

    ticker_treemap_data = tm.getTickerTrends()
    ticker_treemap = Chart('Trend Chart')
    ticker_treemap.getTrendMap(ticker_treemap_data)

    tag_treemap_data = tm.getTagTrends()
    tag_treemap = Chart('Trend Chart')
    tag_treemap.getTrendMap(tag_treemap_data)

    return updated_selected_values, \
            suggested_options, \
            updated_suggestion_values, \
            ticker_treemap.get_chart(), \
            tag_treemap.get_chart()
    


@app.callback(
    Output("suggestions-id", "style"), 
    [Input("suggestions-toggle", "value")]
)

def show_hide_suggestions(toggle_value):
    if toggle_value is None or toggle_value == []:
        return {"display":"none"}
    return {"display":"flex"}


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