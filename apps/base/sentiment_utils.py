from .custom_libraries.mongo_connections import myMongo
import datetime
import pandas as pd

class Sentiment():
    def __init__(self):
        self.tickers = None
        self.get_data()
        self.matched_tickers = ["AAPL", "QQQ.US_5", "GOOG", "MSFT"]
        self.default_matches = ["AAPL", "QQQ.US_5", "GOOG", "MSFT"]

    def get_data(self):
        mongo = myMongo('sentiment')
        db = mongo.db
        sentiment_title = db['sentiment_title']

        self.tickers = sentiment_title.distinct('ticker')
        mongo.close_connection()

    def find_match(self, ticker_part):
        matches = []
        counter = 0
        for ticker in self.tickers:
            if counter == 7: break
            if ticker[:len(ticker_part)] == ticker_part.upper():
                matches.append(ticker)
                counter += 1
        if len(matches) != 0:
            self.matched_tickers = matches
        else:
            self.matched_tickers = self.default_matches
        return matches

    def get_sentiment_data(self, ticker):
        mongo = myMongo('sentiment')
        db = mongo.db
        sentiment_title = db['sentiment_title']
        df = pd.DataFrame(list(sentiment_title.find({'ticker':ticker})))

        # close connection
        mongo.close_connection()

        df.date = df.date.apply(lambda x: datetime.datetime.fromtimestamp(x))
        df.set_index('date',inplace=True, drop=True)
        df.drop(['_id','ticker'],axis=1, inplace=True)
        df = df.loc[datetime.datetime(2019,1,1):]
        df['num_news'] = df.transformers_neg_count_title + df.transformers_pos_count_title
        
        return df

