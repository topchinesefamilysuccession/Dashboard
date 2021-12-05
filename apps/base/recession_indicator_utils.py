import pandas_gbq
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from google.oauth2 import service_account

cred = service_account.Credentials.from_service_account_file('./apps/base/google_key.json')
project_id = 'clever-seat-313815'
dataset = 'us_recession_model.'

def getGaugeSubplotsFig():
    print('Get data from BQ')
    sql_query = f'SELECT index, crisis_in_3m, crisis_in_6m, crisis_in_12m, crisis_in_24m FROM {dataset}best_model_results ORDER BY index DESC LIMIT 2'
    model_results = pandas_gbq.read_gbq(sql_query, 
                                        project_id=project_id,
                                        index_col='index',verbose=None,progress_bar_type=None)
    model_results = round(model_results*100,2)

    fig = make_subplots(rows=1, 
                    cols=4, 
                    specs=[[{'type':'indicator'},{'type':'indicator'},{'type':'indicator'},{'type':'indicator'}]])

    col_number = 1
    for col in model_results:
        fig.add_trace(
            go.Indicator(
                mode = "gauge+number+delta",
                value = model_results[col][0],
                number = { 'suffix': "%" },
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"<b>{col.split('_')[-1].upper()}</b>", 'font':{'size':12}},
                delta = {'reference': model_results[col][0] - model_results[col][1]},
                gauge = {
                    'axis': {'range': [0, 100], 'visible':False},
                    'bar': {'color': "white"},
                    'bgcolor': "white",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 33], 'color': 'green'},
                        {'range': [33, 66], 'color': 'orange'},
                        {'range': [66, 100], 'color': 'red'}],
                    }),
            row=1, col=col_number
        )
        col_number += 1


    layout_config = {
        'autosize':True,
        "paper_bgcolor" : "rgba(0,0,0,0)",
        "plot_bgcolor" : "rgba(0,0,0,0)",
        "margin":{"t":0,"b":0,"l":0,"r":0}
    }

    fig.update_layout(layout_config)

    return fig

def getListOfFactorGroups():
    bq_sql = f'SELECT distinct(A.group) FROM {dataset}factor_groups A'
    factor_groups = pandas_gbq.read_gbq(bq_sql,
                                     credentials=cred,
                                     project_id=project_id,
                                     progress_bar_type=None,
                                     verbose=None)
    return factor_groups.group.to_list()