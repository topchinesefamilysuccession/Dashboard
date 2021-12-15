import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from .base.fred_utils import FredHandler
from .base.charts_utils import Chart, init_chart
from dash import dash_table

import pandas as pd

from app import app

SPINNER = "cube"
table_columns = ["id", "title", "observation_end",  "frequency_short", "notes"]


layout = html.Div([

    html.Div([
        html.H3("Market Research"), 
        dcc.Input(id="search-keyword", value="Inflation"),
        html.P(id="no-result-output"), 
        dcc.Loading(dcc.Graph(id="series-graph"), type=SPINNER),
        html.P(id="description-title", children=["Description"] ),
        html.P(id="report-info"),
        dcc.Checklist(id="table-filters", 
                        options=[
                            {"label":" Sort by Popularity ", "value":"popularity"}, 
                            ], 
                        
                        labelStyle={'display': 'inline-block',"margin-right": "15px", "margin-top": "20px"},
                        ),
        dash_table.DataTable(
                    id="report-table", 
                    columns = [{"id":v, "name":v} for v in table_columns],
                    page_size=14,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    style_table={'width': '100%'},
                    style_header={'textAlign': 'center'},
                    row_selectable = "single",
                    style_cell_conditional=[
                                            {
                                                'if': {'column_id': c},
                                                'textAlign': 'center'
                                            } for c in ['id', 'title',"frequency_short" ]
                                            
                                        ],
                    hidden_columns = ["notes"],
                    css=[{"selector": ".show-hide", "rule": "display: none"}]

                ),
    ], className="markert-search"),
    
        
    
])


@app.callback(
    [Output("report-table", "data"), Output("report-table", "selected_rows"), Output("no-result-output", "children")], 
    [Input("search-keyword", "value"), Input("table-filters", "value")]
)

def fill_table(v, table_filters):
    if v == None:
        raise PreventUpdate

    
    fred_handler = FredHandler()
    rslt = fred_handler.search_report(v)


    if len(rslt) == 0:
        return [{}], [0], ["No results found for the above search keywords."]

    if table_filters != None and len(table_filters) > 0:
        if "popularity" in table_filters:
            rslt = rslt.sort_values(by="popularity", ascending=False)

    rslt = rslt[table_columns]

    return rslt.to_dict("records"), [0], []



@app.callback(
    [Output("report-info", "children")],
    [Input("report-table", "selected_rows")],
    [State("report-table", "data")]

)
def build_description(v, data):
    if v == None:
        raise PreventUpdate


    df = pd.DataFrame(columns = table_columns, data=data)
    index_selected = v[0]

    df = df.iloc[index_selected]
    report_notes = df["notes"]

    return [report_notes]


@app.callback(
    [Output("series-graph", "figure")],
    [Input("report-table", "selected_rows")],
    [State("report-table", "data")]
)

def fill_table(v, data):
    if v == None or data ==None or len(data) == 0:
        raise PreventUpdate

    if len(data[0]) == 0:
        prt_value_fig = Chart("General")
        prt_value_fig.draw_no_data()
        prt_value_fig = prt_value_fig.get_chart()
        return [prt_value_fig]

    df = pd.DataFrame(columns = table_columns, data=data)
    index_selected = v[0]

    df = df.iloc[index_selected]
    report_id = df["id"]
    fred_handler = FredHandler()
    df = fred_handler.get_series(report_id)
    prt_value_fig = Chart("General")
    prt_value_fig.draw_df(df, report_id, "date", "value")
    prt_value_fig = prt_value_fig.get_chart()
    return [prt_value_fig]
