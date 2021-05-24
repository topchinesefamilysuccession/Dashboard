import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from .base.fred_utils import FredHandler
from .base.charts_utils import Chart, init_chart
import dash_table

import pandas as pd

from app import app

table_columns = ["id", "title"]


layout = html.Div([

    html.Div([
        html.H3("Market Research"), 
        dcc.Input(id="search-keyword", value=""), 
        dcc.Graph(id="series-graph"),
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
                    # selected_rows=[0],
                    style_cell_conditional=[
                                            {
                                                'if': {'column_id': c},
                                                'textAlign': 'center'
                                            } for c in ['id', 'title']
                                        ],

                ),
    ], className="markert-search"),
    
        
    
])


@app.callback(
    [Output("report-table", "data")], 
    [Input("search-keyword", "value")]
)

def fill_table(v):
    if v == None:
        raise PreventUpdate
    
    fred_handler = FredHandler()
    rslt = fred_handler.search_report(v)
    print("FRED RESULT")
    print(rslt)
    if len(rslt) == 0:
        return [[{}]]
    rslt = rslt[table_columns]
    return [rslt.to_dict("records")]

@app.callback(
    [Output("series-graph", "figure")],
    [Input("report-table", "selected_rows")],
    [State("report-table", "data")]
)

def fill_table(v, data):
    if v == None or len(data) == 0:
        raise PreventUpdate
    print(data)

    df = pd.DataFrame(columns = table_columns, data=data)
    index_selected = v[0]

    df = df.iloc[index_selected]
    report_id = df["id"]
    fred_handler = FredHandler()
    df = fred_handler.get_series(report_id)
    prt_value_fig = Chart("Portfolio Value")
    prt_value_fig.draw_df(df, report_id, "date", "value")
    prt_value_fig = prt_value_fig.get_chart()
    return [prt_value_fig]
