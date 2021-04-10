import dash_html_components as html
ipsum_lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"


def build_parameters_markdown(parameters):
    rebalancing_frequency, markets, asset_classes,period = parameters[["rebalancing_frequency","markets","asset_classes","period"]].values[0]


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


def build_strategy_summary(stats):
    pnl = stats["pnl"].values[0]
    max_dd = stats["max_dd"].values[0]
    final_portfolio_value =  stats["portfolio_value"].values[0]
    
    summary =  [html.P(children=[
                    html.Strong("PnL: "),
                    f"{pnl:,.2f} $"
                                ]),
                html.P(children=[
                    html.Strong("Max Drawdown: "),
                    f"{max_dd:,.2f} $"
                                ]),
                html.P(children=[
                    html.Strong("Final Portfolio Value: "),
                    f"{final_portfolio_value:,.2f} $"
                                ]),
    
    ]


    return summary