import dash_html_components as html
from dash_table import FormatTemplate
from .custom_libraries.mongo_connections import myMongo


def get_all_xtb_assets():
    db = myMongo("etf")
    df = db.find("etf", "etf_name", "etf_description")
    return df



ipsum_lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"


def build_parameters_markdown(parameters, language="en"):
    if language == "en":
        keys = ["rebalancing_frequency","markets","asset_classes","period"]
    elif language =="cn":
        keys = ["rebalancing_frequency-cn","markets","asset_classes-cn","period"]

    rebalancing_frequency, markets, asset_classes,period = parameters[keys].values[0]


    markdown = [html.P(children=[
                    html.Strong("Rebalancing Frequency: "),
                    html.Br(), 
                    rebalancing_frequency
                                ]),
                html.P(children=[
                    html.Strong("Markets: "), 
                    html.Br(), 
                    markets
                                ]),
                html.P(children=[
                    html.Strong("Asset Classes: "), 
                    html.Br(), 
                    asset_classes
                                ]),
                html.P(children=[
                    html.Strong("Period: "), 
                    html.Br(), 
                    period
                                ]),
                ]
    

    return markdown


def build_strategy_summary(stats, language="en"):
    pnl = stats["pnl"].values[0]
    max_dd = stats["max_dd"].values[0]
    final_portfolio_value =  stats["portfolio_value"].values[0]

    if language == "en":
        pnl_label = "PnL"
        dd_label = "Max Drawdown"
        pv_label = "Final Portfolio Value"
    elif language == "cn":
        pnl_label = "盈亏"
        dd_label = "最大下探"
        pv_label = "最终价值"
    
    summary =  [html.P(children=[
                    html.Strong(f"{pnl_label}: "),
                    f"{pnl:,.2f} $"
                                ]),
                html.P(children=[
                    html.Strong(f"{dd_label}: "),
                    f"{max_dd:,.2f} $"
                                ]),
                html.P(children=[
                    html.Strong(f"{pv_label}: "),
                    f"{final_portfolio_value:,.2f} $"
                                ]),
    
    ]


    return summary


def build_trades_columns(strategies):
    money = FormatTemplate.money(2)
    styled_columns = []

    for i in strategies.get_trades(filter=["S1"]).columns:
        name = i[0].upper() + i[1:]    
        if i in ["price", "value"]:
            styled_column = {"name": name, "id": i, "type":"numeric", "format":money} 
        else:
            styled_column = {"name": name, "id": i} 
        styled_columns.append(styled_column)
    return styled_columns