from .custom_libraries.mongo_connections import myMongo
import datetime
import pandas as pd
from O365 import Account, FileSystemTokenBackend
from tiingo import TiingoClient
import os

TIINGO_TOKEN = "c50cfdc0a109426822e1a16bfa3b473e6a9240ab"
config = {
    'session':True,
    'api_key':TIINGO_TOKEN
}


class Sentiment():
    def __init__(self):
        self.tickers = None
        self.labels_dict = {}
        self.oneDrive = None
        self.news_list = None
        self.tiingoClient = TiingoClient(config)
        self.initial_target_date = None

        self.SignInOneDrive()
        self.get_data()

    def get_data(self):
        mongo = myMongo('sentiment')
        sentiment_title = mongo.db['sentiment_title']

        self.tickers = sentiment_title.distinct('ticker')
        mongo.close_connection()

        self.get_ticker_labels()

    def get_ticker_labels(self):
        mongo = myMongo('etf')
        etfs = mongo.db['etf']
        etfs = pd.DataFrame(list(etfs.find({'etf_name':'etf_description'},{'symbol':1,'description':1,'categoryName':1,'_id':0})))

        for row in etfs.iterrows():
            self.labels_dict[row[1]['symbol']] = {
                'asset_name':row[1]['description'],
                'asset_type':row[1]['categoryName']
            }
         
        etf_comp = mongo.db['etf_components_etfdb']
        for ticker in self.tickers:
            if ticker not in self.labels_dict:
                # Search by exact ticker name
                response = etf_comp.find_one({'Symbol':ticker},{'Holding':1,'_id':0})
                if response is not None:
                    self.labels_dict[ticker] = {
                        'asset_name':response['Holding'],
                        'asset_type':'component'
                        }
                else:
                # Search by partial ticker name
                    response = etf_comp.find_one({'Symbol':{"$regex": ticker}})
                    if response is not None:
                        self.labels_dict[ticker] = {
                            'asset_name':response['Holding'],
                            'asset_type':'component'
                            }
                    else:
                        self.labels_dict[ticker] = {
                            'asset_name':"ticker not found",
                            'asset_type':'ticker not found'
                            }
        mongo.close_connection()

    def get_prices(self, ticker, asset_type='etf',
                    start_date='2019-01-01',end_date = None, 
                    freq='Daily', returns=None):
        if end_date is None:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        if asset_type.lower() == 'etf':
            ticker = ticker.replace('.US_5','')
        df = pd.DataFrame(self.tiingoClient.get_ticker_price(
                ticker,
                startDate=start_date,
                endDate=end_date,
                frequency=freq
            ))
        df = df[['adjClose','date']].copy()
        df.columns = ['close','date']
        df.set_index('date',drop=True,inplace=True)
        if returns is not None:
            df['close'] = round(df.close.pct_change(returns)*100,2)
        return df

    def get_sentiment_data(self, ticker):
        mongo = myMongo('sentiment')
        sentiment_title = mongo.db['sentiment_title']
        df = pd.DataFrame(list(sentiment_title.find({'ticker':ticker})))

        # close connection
        mongo.close_connection()

        df.date = df.date.apply(lambda x: datetime.datetime.fromtimestamp(x))
        df.set_index('date',inplace=True, drop=True)
        df.drop(['_id','ticker'],axis=1, inplace=True)
        df = df.loc[datetime.datetime(2019,1,1):]
        df['num_news'] = df.transformers_neg_count_title + df.transformers_pos_count_title
        self.initial_target_date = df.index[-1].strftime('%Y-%m-%d')

        return df

    def get_news(self, ticker, target_date=None,news_number=50, max_look_back_period=20):
        
        print('Current directory:' + os.getcwd())
        print('Other files:',os.listdir(os.getcwd()))
        print('Does the tnp folder exists here? -',os.path.exists('tmp'))
        # preprocessing
        download_path = 'tmp/'
        if os.path.exists(download_path):
            for filepath in os.listdir(download_path):
                os.remove(download_path + filepath)
            os.removedirs(download_path)
        os.mkdir(download_path)
        
        # TARGET DATE = YYYY-MM-DD

        # Get collection
        mongo = myMongo('sentiment')
        oneDrive_tracker = mongo.db['onedrive_tracker']
        
        if target_date is None:
            target_date = oneDrive_tracker.find_one(sort=[('date',-1)])['date']

        # Create empty DF
        news_df = pd.DataFrame()
        
        #Loop until got 50 news articles
        for i in range(max_look_back_period):
            # Adjust date
            if i != 0:
                new_date = datetime.datetime(int(target_date[:4]),int(target_date[5:7]),int(target_date[8:10])) - datetime.timedelta(days=1)
                target_date = new_date.strftime('%Y-%m-%d')
            
            # Find closest indices
            data = list(oneDrive_tracker.find({'ticker':ticker,'date':target_date},{'_id':0}))
            
            if len(data) != 0:
                df = pd.DataFrame(data)
                df.sort_values(by=['date_hour'], inplace=True, ascending=False)
                
                for file_index in df.id:
                    try:
                        news_file = self.oneDrive.get_item(file_index)
                    except:
                        print('#### OneDrive could not find file with id: ' + file_index)
                        continue
                    news_file.download(download_path)
                    
                    temp_df = pd.read_pickle(download_path + news_file.name)
                    
                    if news_df.empty:
                        news_df = temp_df
                    else:
                        news_df = pd.concat([news_df, temp_df], axis=0, ignore_index=True)
                    
                    if news_df.shape[0] > news_number:
                        mongo.close_connection()
                        self.news_list = news_df.to_dict('records')
        mongo.close_connection()
        self.news_list = news_df.to_dict('records')

    def SignInOneDrive(self):
        client_id = '15731b54-b8cc-4a14-bc6b-b7210a30bb55'
        client_secret = '.R.KN.5Qbr-7ro99o9J~Ptl.3Fb3ZzXfJ9'

        credentials = (client_id, client_secret)

        token_backend = FileSystemTokenBackend(token_path='apps/base/tokens', token_filename='OneDrive_token.txt')
        scope = ['Files.ReadWrite.All','offline_access']

        account = Account(credentials, token_backend=token_backend)

        if not account.is_authenticated:  
            # will check if there is a token and has not expired
            # console based authentication See Authentication for other flows
            # account.authenticate(scopes=scopes)
            # TODO
            # RAISE ERROR - MANUAL AUTHENTICATION REQUIRED
            #raise 'One Drive authentication requires refresh! Please sign in from local instance and copy token to repo.' 
            try:
                if account.authenticate(scopes=scope):
                    print('Authenticated!')    
            except:
                raise 'One Drive authentication requires refresh! Please sign in from local instance and copy token to repo.' 
        
        storage = account.storage() 

        # get the default drive
        self.oneDrive = storage.get_default_drive()

