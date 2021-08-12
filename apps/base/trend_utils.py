import pandas as pd

from datetime import datetime
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



class TrendsMaster():
    def __init__(self):
        self.trend_collection = self.__connectDB()

    def __connectDB(self):
        ''' Establish connections with GCP '''
        cred = credentials.Certificate(os.path.dirname(os.path.realpath(__file__)) + '\\google_key.json')
        firebase_admin.initialize_app(cred)
        # firebase_admin.initialize_app()
        db = firestore.client()
        return db.collection('top_trends')

    def getTickerTrends(self, top_number=20):
        todays_date = datetime.today().date().strftime("%d-%m-%Y")

        query_ref = self.trend_collection.where(u'date',u'==',todays_date).where(u'type',u'==',u'ticker').stream()
        tickers = []
        for doc in query_ref:
            doc_dic = doc.to_dict()
            tickers.append([
                doc_dic['key_word'],
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

        return tickers

    def getTagTrends(self, top_number=20):
        todays_date = datetime.today().date().strftime("%d-%m-%Y")

        query_ref = self.trend_collection.where(u'date',u'==',todays_date).where(u'type',u'==',u'tag').stream()
        tickers = []
        for doc in query_ref:
            doc_dic = doc.to_dict()
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

        return tickers