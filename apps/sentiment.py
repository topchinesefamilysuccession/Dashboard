import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, ALL
from dash.exceptions import PreventUpdate
from dash_html_components.Div import Div
import lorem

import dash

from app import app



from .base.sentiment_utils import Sentiment
from .base.general_utils import ipsum_lorem, build_parameters_markdown, build_strategy_summary
from .base.charts_utils import Chart, init_chart

import json
import datetime

sentiment = Sentiment()

SPINNER = "dot"

def CardGenerator(title='', body_text='', source='', url='', publishedDate=''):

    if title == '':
        title = lorem.sentence()
        body_text = lorem.text()
        source = 'yahoo.com'

    if len(title) > 50:
        title = title[:50] + '...'
    if len(body_text) > 150:
        body_text = body_text[:150] + '...'
    return dbc.Card(
            [
                html.H6(title, className='card-title'),
                dbc.CardBody([
                    html.P(body_text)
                ], className='card-text'),
                dbc.CardFooter([
                    html.P(publishedDate.strftime('%Y-%m-%d %H:%M:%S')),
                    html.A(source, href=url, target="_blank", className='news-url')
                ], className='news-card-footer')
            ],
            className='news-card')

layout = html.Div([

    html.Div(
        [
            html.Div([
                html.H3("Sentiment"),
            ], className='title',
            id='title'),
            html.Div(
                dcc.Dropdown(
                    id='ticker-selection',
                    options=[{'label':value + '     ' + ' | ' + sentiment.labels_dict[value]['asset_name'], 'value':value} for value in sentiment.tickers],
                    value='QQQ.US_5'
                ),
                className='suggestion-div',
                id='suggestion-div'            
            )
        ], 
        className="search-div"
    ),
    html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Dropdown(
                                options=[
                                    {'label':'Bar Chart', 'value':'bar'},
                                    {'label':'Stacked Area Chart', 'value':'area'},
                                    
                                ],
                                value='bar',
                                id='chart-type'
                            ),
                            dcc.Checklist(
                                options=[
                                    {'label':'Mean trend','value':'mean'}
                                ],
                                value=[],
                                id='mean-trend'
                            ),
                            html.Div(
                                children=[
                                    dcc.Checklist(
                                        options=[
                                            {'label':'Add Price','value':'price'}
                                        ],
                                        value=[],
                                        id='price-checkbox'
                                    ),
                                    dcc.Checklist(
                                        options=[
                                            {'label':'Returns','value':'returns'}
                                        ],
                                        value=[],
                                        id='returns-checkbox',
                                        style={'visibility':'hidden'}
                                    ),
                                    dcc.Dropdown(
                                        options=[
                                            {'label':'Daily', 'value':'1'},
                                            {'label':'Weekly', 'value':'5'},
                                            {'label':'Monthly', 'value':'21'},
                                            {'label':'Quarterly', 'value':'63'},
                                        ],
                                        value='1',
                                        id='returns-type',
                                        style={'width':100, 'visibility':'hidden'}
                                    ),
                                ],
                                id='price-controls'
                            )
                            
                        ],
                        id='graph-controls'
                    ),
                    dcc.Loading(dcc.Graph(id="sentiment-chart"), type=SPINNER)
                ],
                id='sentiment-graph'
            ),
            html.Div(
                [   
                    html.Div(
                        children=[
                            html.H4('News feed', id='news_feed_title')
                        ],
                        className="news-list-title"
                    ),
                    dcc.Loading(html.Div(id='news-list'), type=SPINNER)
                ],
                id='sentiment-news'
            ),
        ],
        className='news-container'
    )

], className='sentiment-div')

@app.callback(
    [
        Output('sentiment-chart',"figure"),
        Output('title','children'),
        Output('chart-type','options'),
        Output('mean-trend','options'),
        Output('news_feed_title','children'),
        Output('price-controls','children'),
        Output('news-list','children')
    ],
    [
        Input('ticker-selection','value'),
        Input('sentiment-chart','relayoutData'),
        Input('chart-type','value'),
        Input('mean-trend','value'), 
        Input('language','value'),
        Input('price-checkbox','value'),
        Input('returns-checkbox','value'),
        Input('returns-type','value')
    ]
    )

def render_Page(ticker, relayoutData, chart_type, mean_trend, language,price_checkbox,returns_checkbox,returns_type):
    if ticker == None:
        raise PreventUpdate
    
    if language == ["cn"]:
        language = "cn"
    else:
        language = "en"

    if language == "cn":
        section_title = '??????'
        chart_options = [
                            {'label':'?????????','value':'bar'},
                            {'label':'???????????????','value':'area'}
                        ]
        mTrend_options = [
                            {'label':'?????????','value':'mean'}
                        ]
        news_feed_title = '????????????'
    else:
        section_title = 'Sentiment'
        chart_options = [
                            {'label':'Bar Chart','value':'bar'},
                            {'label':'Stacked area','value':'area'}
                        ]
        mTrend_options = [
                            {'label':'Mean trend','value':'mean'}
                        ]
        news_feed_title = 'News Feed'


    if len(mean_trend) != 0:
        mean_trend = True
    else:
        mean_trend = False

    returns_checked = []
    if len(price_checkbox) != 0:
        pr_visible = 'visible'
        price_checked = ['price']
        
        if len(returns_checkbox) != 0:
            returns_checked = ['returns']
            price_df = sentiment.get_prices(ticker,sentiment.labels_dict[ticker]['asset_type'],returns=int(returns_type))
        else:
            price_df = sentiment.get_prices(ticker,sentiment.labels_dict[ticker]['asset_type'])
            
    else:
        pr_visible = 'hidden'
        price_checked = []
        price_df = []

    price_returns_controls = [dcc.Checklist(
                                        options=[
                                            {'label':'Add Price','value':'price'}
                                        ],
                                        value=price_checked,
                                        id='price-checkbox'
                                    ),
                                    dcc.Checklist(
                                        options=[
                                            {'label':'Returns','value':'returns'}
                                        ],
                                        value=returns_checked,
                                        id='returns-checkbox',
                                        style={'visibility':pr_visible}
                                    ),
                                    dcc.Dropdown(
                                        options=[
                                            {'label':'Daily', 'value':1},
                                            {'label':'Weekly', 'value':7},
                                            {'label':'Monthly', 'value':21},
                                            {'label':'Quarterly', 'value':63},
                                        ],
                                        value=returns_type,
                                        id='returns-type',
                                        style={'width':100, 'visibility':pr_visible}
                                    ),
                                ]

    df = sentiment.get_sentiment_data(ticker)
    sentiment_chart = Chart('Sentiment', multiple_axes=True)

    if 'xaxis.range[0]' in relayoutData:
        sentiment_chart.draw_sentiment_chart(df, chart_type=chart_type,
                                            dates=[relayoutData['xaxis.range[0]'].split(' ')[0],relayoutData['xaxis.range[1]'].split(' ')[0]],
                                            mean_trend=mean_trend, price_graph=price_df)
        sentiment.get_news(ticker,relayoutData['xaxis.range[1]'].split(' ')[0])
    else:
        #sentiment.get_news(ticker=ticker, target_date=sentiment.initial_target_date)
        sentiment_chart.draw_sentiment_chart(df, chart_type=chart_type, mean_trend=mean_trend, price_graph=price_df)
        sentiment.get_news(ticker)
    
    news_list = [CardGenerator(x['title'],x['description'],x['source'],x['url'],x['publishedDate']) for x in sentiment.news_list]

    sentiment_fig = sentiment_chart.get_chart()

    return sentiment_fig,\
            section_title,\
            chart_options,\
            mTrend_options,\
            news_feed_title, \
            price_returns_controls, \
            news_list
