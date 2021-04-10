import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from app import app

from .base.strategies_utils import Strategies
from .base.general_utils import ipsum_lorem, build_parameters_markdown, build_strategy_summary
from .base.charts_utils import Chart, init_chart


SPINNER = "cube"
# 'graph', 'cube', 'circle', 'dot', 'default'



strategies = Strategies()

layout = html.Div([
    
    html.Div([
        html.Div([
                html.H4("Strategies"),
                dcc.Dropdown(id="strategies-list",
                options = [{"label":k,"value":v} for k,v in strategies.get_strategies_names().items()], 
                value="S1"
                )
            ], className="strategies-div"),
 
            html.Div([
                dcc.Tabs([
                    dcc.Tab(className="custom-tab",label="Description", id="description-tab", children=[
                        dcc.Markdown("", id="strategies-description")
                    ]),
                    dcc.Tab(className="custom-tab",label="Parameters", id="paremeters-tab", children=[
                        html.Div(children=["rebalancing_frequency,markets,ac,period"], id="strategies-parameters")
                    ]),
                    dcc.Tab(className="custom-tab",label="Other", id="others-tab", children=[
                        html.P("Not Sure")
                    ])
                ], className="custom-tabs")
            ], className="main-stats-div"),
    ],className="left-side"),
    


    html.Div([
        
        html.Div([
                html.Div([html.H3("Drawdown: 2%", id="drawdown-percent")]),
                html.Div([html.H3("PnL: 20%", id="pnl-percent")]),
               
            ], className="summary-div"),

            html.Div([
                dcc.Checklist(id="graphs-options", 
                options=[
                    {"label":" SP500 ", "value":"SP500"}, 
                    {"label":" 1-3 Year Treasury Bonds ", "value":"Bonds"},
                    {"label":" Gold ", "value":"Gold"},
                    {"label":" VIX ", "value":"VIX"},
                    
                    ], 
                
                labelStyle={'display': 'inline-block',"margin-right": "15px", "margin-top": "20px"},
                ),

                html.Div([
                        html.Div([
                        dcc.Loading(dcc.Graph(id="main-chart"), type=SPINNER)
                    ], className="left-chart-div"),

                        html.Div([
                            html.Div("PnL", id="strategies-summary"), 
                            dcc.Loading(dcc.Graph(id="assets-pie", config={'displayModeBar': False}), type=SPINNER)
                            
                        ], className="right-chart-div")

                ], className="charts-content")
                
              
            ], className="charts-div")
    ], className="right-side")
    


], className="backtesting-content")


@app.callback(
    [Output("strategies-description", "children"), Output("strategies-parameters", "children"), Output("pnl-percent", "children"), 
    Output("drawdown-percent", "children"), Output("main-chart", "figure"), 
    Output("strategies-summary", "children"), Output("assets-pie", "figure"), 
    Output("description-tab", "label"), Output("paremeters-tab", "label"), Output("others-tab", "label")],
    [Input("strategies-list", "value"), Input("graphs-options", "value"), Input("language", "value")]
)

def render_strategies_description(strategy_id, graphs_options, language):
    if strategy_id == None:
        raise PreventUpdate
    
    if language == ["cn"]:
        language = "cn"
    else:
        language = "en"
    
    #Descriptions and Parameters
    descriptions = strategies.get_strategies_details(details="description", filter=[strategy_id], language=language)

    if language == "cn":
        desc_key = "strategy_description-cn"
        pnl_label = "盈亏"
        dd_label = "下探"
    else:
        desc_key = "strategy_description"
        pnl_label = "PnL"
        dd_label = "Drawdown"

    descriptions_markdown = descriptions[desc_key].values[0]
    
    parameters = strategies.get_strategies_details(details="parameters", filter=[strategy_id], language=language)
    
    parameters_markdown = build_parameters_markdown(parameters, language)


    #PnL and Dradown
    stats = strategies.get_strategies_stats(filter=[strategy_id])

    
    pnl = f"{pnl_label}: {stats['percentual_pnl'].values[0] * 100:.2f}%"
    dd = f"{dd_label}: {stats['percentual_dd'].values[0] * 100:.2f}%"

    # Strategy Summary

    strategy_summary = build_strategy_summary(stats, language)

    #Portfolio Value Chart
    prt_value = strategies.get_strategies_portfolio_value(filter=[strategy_id])

    prt_value_fig = Chart("Portfolio Value")
    prt_value_fig.draw_portfolio_value(prt_value, strategy_id)

    #Adding BenchMark charts
    if graphs_options:
        for opt in graphs_options:
            prt_value_benchmark = strategies.get_strategies_portfolio_value(filter=[opt])
            prt_value_fig.draw_portfolio_value(prt_value_benchmark, opt)
        

    prt_value_fig = prt_value_fig.get_chart()

    #Assets Pie Chart
    
    assets_pie_fig = Chart("Pie Chart")
    assets_distributions = strategies.get_assets_mean_distribution(filter=[strategy_id])
    
    assets_pie_fig.draw_pie_chart(assets_distributions)


    assets_pie_fig = assets_pie_fig.get_chart()

    if language == "en":
        description_tab = "Description" 
        paramenters_tab = "Parameters"
        others_tab = "Other"
    elif language == "cn":
        description_tab = "简介" 
        paramenters_tab = "指标参数"
        others_tab = "其他"

    return descriptions_markdown, parameters_markdown, pnl, dd, prt_value_fig, strategy_summary,assets_pie_fig, description_tab, paramenters_tab, others_tab


