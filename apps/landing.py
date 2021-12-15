from logging import PercentStyle
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from .base.charts_utils import Chart, init_chart
from .base.api_handler import StrategiesAPI
from .base.trend_utils import TrendsMaster
from .base.general_utils import get_all_xtb_assets, get_ETF_from_component
from .base.recession_indicator_utils import getGaugeSubplotsFig, getListOfFactorGroups, getGaugeListOfFigs, getRecessionHistGraph, getLMCards
import pandas as pd
from app import app
from datetime import datetime

df = get_all_xtb_assets()
tm = TrendsMaster()

def getTickerTreeMap():
    ticker_treemap_data = tm.getTickerTrends()
    ticker_treemap = Chart('Trend Chart')
    """SENTIMENT INVESTOR"""
    # ticker_treemap.getTrendMap(ticker_treemap_data,'ticker','mentions','sentiment')
    """"""
    ticker_treemap.getTrendMap(ticker_treemap_data,'keyword','news_count','aggregate_score')
    return ticker_treemap.get_chart()

def getTagTreeMap():
    tag_treemap_data = tm.getTagTrends()
    tag_treemap = Chart('Trend Chart')
    tag_treemap.getTrendMap(tag_treemap_data,'keyword','news_count','aggregate_score')
    return tag_treemap.get_chart()

tickerTreeMap = getTickerTreeMap()
tagTreeMap = getTagTreeMap()

list_of_assets = df["keywords"].unique()

factor_groups = getListOfFactorGroups()
rebuild_btn = html.Button('Rebuild', id='btn-rebuild', className='btns-general')

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
            html.H2('Daily Sentiment Top Trends'),
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
                    id='ticker_graph',
                    responsive=True),
                ], className='ticker-trend'),
                html.Div([
                    dcc.Graph(figure=tagTreeMap,
                                config={
                                    'displayModeBar':False
                                },
                                clear_on_unhover=True,
                    id='tag_graph',
                    responsive=True),
                ], className='tag-trend'),
            ], className='trend-graphs-container')
        ])
    ], className='sentiment-trends'),
    html.Div([
        html.Div([
            html.H2('Recession Indicator')
        ], className='recession-indicator-title'),
        dcc.Loading(children=[
            html.Div([
                html.Div([
                    html.H4('Factors used in a model'),
                    html.Div(children=[
                        html.Div([
                            html.Div([
                                html.Button('Unselect all', id='btn-selectall-factors', className='btns-general')
                            ],id='btn-selectall-container'),
                            html.Div(id='btn-rebuild-container'),
                        ], className='fct-btns-container'),
                        dcc.Checklist(
                            options=[{'label':x, 'value':x} for x in factor_groups],
                            value=factor_groups,
                            labelClassName="fg-item",
                            id='factor-checklist'
                        )
                    ])
                ], className='fct-list-container'),
                html.Div([
                    html.Div([
                        html.H4('Probability of US recession within 3M')]),
                    html.Div([
                        html.Div([
                            dcc.Graph(figure=getRecessionHistGraph(), responsive=True)
                        ],className='rec-trend-chart'),
                        html.Div(children=[
                            html.Div([
                            dcc.Graph(
                                figure=fig,
                                config={
                                    'displayModeBar':False
                                },
                                responsive=True,
                            )],className="gauge-fig") for fig in getGaugeListOfFigs()], className="gauge-fig-container")
                        ], className='rec-charts')
                ], className='recession-charts-container')
            ], className='recession-factors-container'),
            html.Div([
                html.H4('Largest movers'),
                html.Div(children=getLMCards(), className='lm-cards-container')
            ], className='largest-movers-container')
        ])
    ], className='recession-model-container'),
    html.Div(className='free-space'),
    html.Div([
        html.P('Created by TCFS amazing dev team ' + u"\u00AE")
    ], className='main-footer')
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
    [
        Output('btn-rebuild-container','children'),
        Output('btn-selectall-factors','children'), 
        Output("factor-checklist","value")
    ],
    [
        Input('factor-checklist','value'),
        Input('btn-selectall-factors','n_clicks')
    ],
    [
        State('btn-selectall-factors','children'),
        State('factor-checklist','options')
    ]
)

def manageFactorChecklist(fct_chk_values,btn_selectall_clicks,
                            btn_selectall_text, fct_checklist_options):

    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    all_options = [x['value'] for x in fct_checklist_options]
    if button_id == 'btn-selectall-factors':
        if btn_selectall_text[0] == 'Select all':
            if len(set(all_options) - set(factor_groups)):
                return [rebuild_btn], ['Unselect all'], all_options
            else:
                return [html.Div()], ['Unselect all'], all_options
        else:
            return [html.Div()], ['Select all'], []
    
    if len(set(factor_groups) - set(fct_chk_values)):
        return [rebuild_btn], ['Select all'], fct_chk_values
    else:
        return [html.Div()], ['Unselect all'], fct_chk_values




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