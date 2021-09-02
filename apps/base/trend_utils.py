import pandas as pd

from datetime import datetime
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from .custom_libraries.mongo_connections import myMongo

class TrendsMaster():
    def __init__(self):
        print('Initiate trend master!')
        self.trend_collection = self.__connectDB()
        self.tag_stop_words = set([
            'tiingo_top','stock','unknown_sector','ap','general'
        ])
        self.db = myMongo('etf')

    def tickerFilter(self, ticker):
        '''Filter top tickers by ones that exists in ETFs portfolio'''
        return self.db.check_if_exists('etf_components_etfdb','Symbol',ticker)

    def __connectDB(self):
        ''' Establish connections with GCP '''
        if os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + '\\google_key.json'):
            cred = credentials.Certificate(os.path.dirname(os.path.realpath(__file__)) + '\\google_key.json')
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
        db = firestore.client()
        return db.collection('top_trends')

    def getTickerTrends(self, top_number=27):
        # todays_date = datetime.today().date().strftime("%d-%m-%Y")
        todays_date = '14-08-2021'

        query_ref = self.trend_collection.where(u'date',u'==',todays_date).where(u'type',u'==',u'ticker').stream()
        tickers = []
        for doc in query_ref:
            doc_dic = doc.to_dict()
            
            # Tag filter for stop words
            # print(f"Check if ticker {doc_dic['key_word'].upper()} passes filter rule {self.tickerFilter(doc_dic['key_word'].upper())}")
            if self.tickerFilter(doc_dic['key_word'].upper()):
                # print(f"Check if ticker {doc_dic['key_word'].upper()} passes filter rule")
                tickers.append([
                    doc_dic['key_word'],
                    doc_dic['title_positive_score'],
                    doc_dic['title_negative_count'],
                    doc_dic['title_positive_count'],
                    doc_dic['title_negative_score'],
                    doc_dic['news_count'],
                    doc_dic['title_aggregate_score']
                ])
        
        self.db.close_connection()

        tickers = pd.DataFrame(tickers, columns=['keyword','title_positive_score','title_negative_count','title_positive_count','title_negative_score','news_count','title_aggregate_score'])
        tickers.sort_values(by=['news_count'], ascending=False, inplace=True)
        tickers = tickers.iloc[:top_number]
        # print(tickers)
        return tickers

    def getTagTrends(self, top_number=27):
        # todays_date = datetime.today().date().strftime("%d-%m-%Y")
        todays_date = '14-08-2021'

        query_ref = self.trend_collection.where(u'date',u'==',todays_date).where(u'type',u'==',u'tag').stream()
        tickers = []
        for doc in query_ref:
            doc_dic = doc.to_dict()
            # Tag filter for stop words
            # print(f"Check if tag {doc_dic['key_word']} passes filter rule {not doc_dic['key_word'] in self.tag_stop_words}")
            if not doc_dic['key_word'] in self.tag_stop_words:
                tickers.append([
                    doc_dic['key_word'].replace('_',' ').capitalize(),
                    doc_dic['title_positive_score'],
                    doc_dic['title_negative_count'],
                    doc_dic['title_positive_count'],
                    doc_dic['title_negative_score'],
                    doc_dic['news_count'],
                    doc_dic['title_aggregate_score']
                ])
        
        tickers = pd.DataFrame(tickers, columns=['keyword','title_positive_score','title_negative_count','title_positive_count','title_negative_score','news_count','title_aggregate_score'])
        tickers.sort_values(by=['news_count'], ascending=False, inplace=True)
        tickers = tickers.iloc[:top_number]
        # print(tickers)

        return tickers