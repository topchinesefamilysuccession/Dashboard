import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
from .base.macro_utils import MacroTable
from app import app

macro_table = MacroTable("inflation")
macro_table.load_reports()
reports = macro_table.get_measure_from_reports("all")


table_columns = ["report", "current", "previous", "Y-1", "Y-2"]

layout = html.Div([

    html.Div([
         dash_table.DataTable(
                    id="inflation-table", 
                    columns = [{"id":v, "name":v} for v in reports.columns],
                    data=reports.to_dict("records"), 
                    page_size=14,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    style_table={'width': '100%'},
                    style_header={'textAlign': 'center'},
                    row_selectable = "single",
                    css=[{"selector": ".show-hide", "rule": "display: none"}]
                ),
    ], className="inflation-table")
    
])