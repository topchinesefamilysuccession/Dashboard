import dash
import dash_bootstrap_components as dbc
from dash import html

import datetime
import pandas_gbq
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from google.oauth2 import service_account

# cred = service_account.Credentials.from_service_account_file('./apps/base/google_key.json')
project_id = 'clever-seat-313815'
dataset = 'us_recession_model.'

def getGaugeSubplotsFig():
    print('Get data from BQ')
    sql_query = f'SELECT index, crisis_in_3m, crisis_in_6m, crisis_in_12m, crisis_in_24m FROM {dataset}best_model_results ORDER BY index DESC LIMIT 2'
    model_results = pandas_gbq.read_gbq(sql_query, 
                                        project_id=project_id,
                                        index_col='index',
                                        verbose=None,
                                        progress_bar_type=None)
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
                        {'range': [0, 33], 'color': 'rgba(0,178,118,1)'},
                        {'range': [33, 66], 'color': 'orange'},
                        {'range': [66, 100], 'color': 'rgba(229,57,53,1)'}],
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

def getGaugeListOfFigs():
    print('Get data from BQ')
    sql_query = f'SELECT index, crisis_in_3m, crisis_in_6m, crisis_in_12m, crisis_in_24m FROM {dataset}best_model_results ORDER BY index DESC LIMIT 2'
    model_results = pandas_gbq.read_gbq(sql_query, 
                                        project_id=project_id,
                                        index_col='index',
                                        verbose=None,
                                        progress_bar_type=None)
    model_results = round(model_results*100,2)

    figs = []

    layout_config = {
        'autosize':True,
        "paper_bgcolor" : "rgba(0,0,0,0)",
        "plot_bgcolor" : "rgba(0,0,0,0)",
        "margin":{"t":0,"b":0,"l":0,"r":0},
    }

    for col in model_results:
        fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = model_results[col][0],
                number = { 'suffix': "%" },
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"<b>{col.split('_')[-1].upper()}</b>", 'font':{'size':12}},
                delta = {'reference': model_results[col][0] - model_results[col][1], 
                        'increasing': {'color': "rgba(229,57,53,1)"},
                        'decreasing': {'color': "rgba(0,178,118,1)"}},
                gauge = {
                    'axis': {'range': [0, 100], 'visible':False},
                    'bar': {'color': "red"},
                    'bgcolor': "white",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 33], 'color': 'rgba(0,178,118,1)'},
                        {'range': [33, 66], 'color': 'orange'},
                        {'range': [66, 100], 'color': 'rgba(229,57,53,1)'}],
                    }))
        fig.update_layout(layout_config)
        figs.append(fig)
    return figs

def getListOfFactorGroups():
    bq_sql = f'SELECT distinct(A.group) FROM {dataset}factor_groups A'
    factor_groups = pandas_gbq.read_gbq(bq_sql,
                                        project_id=project_id,
                                        progress_bar_type=None,
                                        verbose=None)
    return factor_groups.group.to_list()

def getRecessionHistGraph(feature='3m'):
    print('Get data from BQ')
    sql_query = f'SELECT index, crisis, crisis_in_{feature} FROM {dataset}best_model_results ORDER BY index DESC'
    model_results = pandas_gbq.read_gbq(sql_query, 
                                        project_id=project_id,
                                        index_col='index', verbose=None,progress_bar_type=None)
    model_results = round(model_results*100,2)
    model_results.index = pd.to_datetime(model_results.index)
    model_results.sort_index(inplace=True)
    model_results = model_results.loc[datetime.date(1995,1,1):,:]
    model_results.reset_index(inplace=True)
    model_results.rename(columns={'index':'date',f'crisis_in_{feature}':'rec_prob'},inplace=True)
    model_results.rec_prob = model_results.rec_prob.ewm(5).mean()

    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=model_results['date'], 
                    y=model_results.crisis,
                    mode='none',
                    fill='tozeroy',
                    fillcolor='lightgrey',
                    name='Historical recessions'
                    )
                )

    fig.add_trace(go.Scatter(x=model_results['date'], 
                    y=model_results.rec_prob, 
                    mode='lines',
                    fill='tozeroy',
                    line=dict(width=1,color='rgba(229,57,53,1)'),
                    name=f'Probability'
                    )
                )

    layout_config = {
        'autosize':True,
        "paper_bgcolor" : "rgba(0,0,0,0)",
        "plot_bgcolor" : "rgba(0,0,0,0)",
        "margin":{"t":0,"b":0,"l":0,"r":0},
        "yaxis_range":[0,max([1,model_results.rec_prob.max()+10])],
        "legend":{
            "yanchor":"top",
            "y":0.99,
            "xanchor":"left",
            "x":0.01
            }
        }

    fig.update_layout(layout_config)
    return fig


def get_LM_Card(factor_name, move_v, beta_v, delta_v):

    trl_up = u"\u25B2"
    trl_down = u"\u25BC"
    beta = u"\u03B2"
    delta = u"\u0394"

    card_id = factor_name.lower()
    trl_up_c = html.Span(trl_up, className='trl-up')
    trl_down_c = html.Span(trl_down, className='trl-down')

    move_symbol = trl_up_c if move_v > 0 else trl_down_c
    delta_symbol = trl_up_c if delta_v > 0 else trl_down_c
    container_type = 'lm-container-green' if move_v > 0 else 'lm-container-red'

    description = f'The factor change from previous period is {str(delta_v)}%, the importance factor factored derived by the model is {str(beta_v)}.\nThe overall impact, which is a product of latest two, is equal to {str(move_v)}%'

    factor_name = factor_name.replace('_',' ')
    card = html.Div([
                html.Div([
                    html.Span(factor_name)
                ], className='lm-title-container'),
                html.Div([
                    move_symbol,
                    html.Span(str(move_v) + '%')
                ],className='lm-overall-container'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(beta + ': '),
                            html.Span(str(beta_v))
                        ],className='lm-beta-container'),
                        html.Div([
                            html.Span(delta + ': '),
                            delta_symbol,
                            html.Span(str(delta_v) + '%')
                        ], className='lm-delta-container')
                    ], className='lm-breakdown-data'),
                    html.Div([
                        html.Span(u"\U0001F6C8", id=card_id),
                        dbc.Tooltip(description,
                            target=card_id,
                            placement='right',
                            class_name='tt_description')
                    ], className='lm-info')
                ], className='lm-change-breakdown-container'),
            ],className='lm-container ' + container_type)
    return card

def getLMCards():
    sql_query = f'SELECT index, crisis_in_3m_x_change, crisis_in_3m_x_imp_svm, crisis_in_3m_x_combined FROM {dataset}largest_movers ORDER BY index DESC'
    model_results = pandas_gbq.read_gbq(sql_query,
                                        project_id=project_id,
                                        progress_bar_type=None,
                                        verbose=None)

    model_results = model_results.round(4)
    abs_col = model_results.columns[-1] + 'abs'
    model_results[abs_col] = abs(model_results[model_results.columns[-1]])
    model_results.sort_values(by=[abs_col], ascending=False, inplace=True)

    list_of_cards = []

    for index, row in model_results.iterrows():
        list_of_cards.append(get_LM_Card(row[0],row[3],row[2],row[1]))

    return list_of_cards
        
