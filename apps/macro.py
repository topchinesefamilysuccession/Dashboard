import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_table
from .base.macro_utils import MacroTable
from .base.mappings.macro_tables_mapping import get_tables_mapping
from app import app

# macro_table = MacroTable("inflation")
# macro_table.load_reports()
# reports = macro_table.get_measure_from_reports("all")
# table_columns = ["report", "current", "previous", "Y-1", "Y-2"]
# print(reports)

layout = html.Div([
        html.Div(id="all-tables"),
        html.P(id="test")
        ])


@app.callback(
    [Output("all-tables", "children")],
    [Input("url", "pathname")]
)

def test(v):
    if v != "/apps/macro":
        raise PreventUpdate

    macro_indicators = get_tables_mapping("macro_indicators")

    div_list = []
    
    for macro_indicator in macro_indicators:
        macro_name_cased = macro_indicator[0].upper() + macro_indicator[1:]
        print(macro_name_cased)
        macro_table = MacroTable(macro_indicator)
        macro_table.load_reports()
        reports = macro_table.get_measure_from_reports("all")

        div_list.append([html.Div([
            html.H4(macro_name_cased),
            dash_table.DataTable(
                    id=f"{macro_indicator}-table", 
                    columns = [{"id":v, "name":v} for v in reports.columns],
                    data=reports.to_dict("records"), 
                    page_size=7,
                    filter_action="none",
                    # sort_action="native",
                    # sort_mode="multi",
                    style_table={'width': '100%'},
                    style_header={'textAlign': 'center'},
                    css=[{"selector": ".show-hide", "rule": "display: none"}]
                ),

        ], className=f"{macro_indicator}-table")])



    return [div_list[0]]

