import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc


import dash_table
import pandas as pd

from .base.strategies_utils import Strategies
from .base.simulation_utils import Simulation
from .base.charts_utils import Chart, init_chart
from .base.general_utils import get_all_xtb_assets

from app import app
import json

import plotly.express as px

general_strategies = Strategies()

all_assets = get_all_xtb_assets()


def fix_country_list(rslt):
    dict_01 = {}
    for k,v in rslt.items():
        splited_country = k.split(",")
        if len(splited_country) > 1:
            splited_country = [c.strip() for c in splited_country]
            dict_01.update(dict(zip(splited_country, [((v / len(splited_country)))] * len(splited_country))))
        else:
            dict_01.update({k:v})

    return dict_01


modal = html.Div(
    [
        dbc.Button("Simulation", id="open", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader("Header"),
                dbc.ModalBody("This is the content of the modal"),
                dcc.Graph(id="simulation-graph"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ml-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            is_open=False,
        ),
    ]
)



def load_strategy(data_dict):

    strategies = Strategies(data_dict)
    df = strategies.get_strategies_portfolio_value(daily_change=True)
    
    prt_value_fig = Chart("Portfolio Value")
    prt_value_fig.draw_portfolio_value(df, "Portfolio Value")

    assets_pie_fig = Chart("Pie Chart")
    assets_distributions = strategies.get_assets_mean_distribution()
    assets_pie_fig.draw_pie_chart(assets_distributions)
    
    df = strategies.get_assets_mean_distribution(top_size=None, as_df=True)

    
    df['weight'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df["values"]], index = df.index)


    translator_df = all_assets[all_assets["symbol"].isin(df["assets"].values)][["symbol", "keywords","Region (Specific)"]]

    df["asset_translation"] = df["assets"].apply(lambda x: "cash" if x == "cash" else translator_df[translator_df["symbol"] == x]["keywords"].values[0]) 

    df["country"] = df["assets"].apply(lambda x: "cash" if x == "cash" else translator_df[translator_df["symbol"] == x]["Region (Specific)"].values[0])


    df_map = df
    df_map["weight_decimal"] = df_map["weight"].apply(lambda x: float(x.split("%")[0])/ 100)
    rslt = df[(~df["country"].isna()) & (df["country"] != "cash")][["weight_decimal", "country"]].groupby(by=["country"]).sum().to_dict()["weight_decimal"]
    rslt = fix_country_list(rslt)
    df_map = pd.DataFrame( columns=["country"], data=list(rslt.values()), index=rslt.keys())
    df_map["country"] = df_map["country"]



    df.drop("values", axis=1, inplace=True)

    stats_pnl = strategies.get_strategies_stats()
    
    prt_value_figure = prt_value_fig.get_chart()
    distribution_pie_figure = assets_pie_fig.get_chart()

    trades = strategies.get_trades()


    layout = html.Div([

        dcc.Loading(modal),    
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
                        dcc.Loading(dcc.Graph(id="main-chart", figure =prt_value_figure))
                        ], className="left-chart-div"),
                html.Div([
                        dcc.Loading(dcc.Graph(id="assets-pie", config={'displayModeBar': False}, figure=distribution_pie_figure))
                        ], className="right-chart-div")
                        ], className="charts-content"),

        ]),



        html.Div([
            html.Div([
                                dash_table.DataTable(
                                id="backtesting-results", 
                                columns = [{"id":v, "name":v} for v in df.columns],
                                data=df.to_dict("records"), 
                                page_size=7,            
                                style_table={'width': '100%', 'overflowY': 'scroll'},
                                style_header={'textAlign': 'center'},
                                css=[{"selector": ".show-hide", "rule": "display: none"}],
                                ) 
                    ], className="results"),

            html.Div(
                [
                html.P(f"PnL: {(stats_pnl['percentual_pnl'].values[0] * 100):.2f}%"),
                html.P(f"DrawDown: {(stats_pnl['percentual_dd'].values[0] * 100):.2f}%"),
                html.P(f"DrawDown: {stats_pnl['max_dd'].values[0]}"),
                ], 
            



        )], id="stats"), 


        dcc.Graph(figure = px.scatter_geo(df_map, locations=df_map.index, color=df_map.index,
                    hover_name=df_map.index, size="country",
                    projection="natural earth")),

        # html.Div([
        #     html.H4("Trades Report", id="trades-report-header"),
        #     html.Div([
        #         dash_table.DataTable(
        #             id="trades-table", 
        #             columns =  [{"id":v, "name":v} for v in trades.columns],
        #             data = trades.to_dict("records"),
        #             page_size=14,
        #             filter_action="native",
        #             sort_action="native",
        #             sort_mode="multi",
        #             export_format="csv", 
        #             style_table={'width': '100%'},
        #             style_header={'textAlign': 'center'},
        #             style_cell_conditional=[
        #                                     {
        #                                         'if': {'column_id': c},
        #                                         'textAlign': 'center'
        #                                     } for c in ['date', 'symbol']
        #                                 ],
        #         ) 
        #     ], className="trades-table-div")

        # ], className="trades-content"),
        
    ])

    return layout




@app.callback(
    [Output("main-chart", "figure")],
    [Input("graphs-options", "value"), 
    State("store", "data")]
)

def render_strategies_description(graphs_options, data_dict):

    if not graphs_options:
        raise PreventUpdate

    strategies = Strategies(data_dict)
    df = strategies.get_strategies_portfolio_value(daily_change=True)
    
    prt_value_fig = Chart("Portfolio Value")
    prt_value_fig.draw_portfolio_value(df, "Portfolio Value")
    
    if graphs_options:
        for opt in graphs_options:
            prt_value_benchmark = general_strategies.get_strategies_portfolio_value(filter=[opt])
            prt_value_fig.draw_portfolio_value(prt_value_benchmark, opt)
        
    prt_value_fig = prt_value_fig.get_chart()

    return  [prt_value_fig]



@app.callback(
    [Output("modal", "is_open"), Output("simulation-graph", "figure")],
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open"), State("backtesting-results", "data")],
)
def toggle_modal(n1, n2, is_open, backtesting_data):
    if n1 or n2:
        df = pd.DataFrame(columns = ['assets', 'weight', 'asset_translation', 'country', 'weight_decimal'], data=backtesting_data)
        print([x for x in df["assets"].values[1:]],[float(x[:-1])/100 for x in df["weight"].values[1:]])
        simulation = Simulation([x for x in df["assets"].values[1:]],[float(x[:-1])/100 for x in df["weight"].values[1:]])
        print(simulation.get_results())
        return not is_open, {}
        
    return is_open, {}