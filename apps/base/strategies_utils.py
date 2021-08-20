from .custom_libraries.mongo_connections import myMongo
import pandas as pd

backtesting_strategies = {
    "S1 - Benchmark": "S1",
    "S3 - Institutional holders":"S3",
    "S4 - Deep Learning Best Performers":"S4",
    "S5 - DNN SMA Markowitz Allocation":"S5"
}

class Strategies():
    def __init__(self, data_dict = None):
        self.strategies_description = None
        self.strategies_general_stats = None
        if data_dict is None:
            self.get_strategies_dfs()
        else:
            self.build_df_from_data_dict(data_dict)

    
    def _filter_df_by_id(self, df, filter):
        if type(filter) != list:
            raise ValueError("Please pass filter as a list")
        df = df[df["strategy_id"].isin(filter)]
        return df
    
    def build_df_from_data_dict(self, data_dict):
        self.strategies_general_stats = pd.read_json(data_dict.get("stats"))
        self.strategies_portfolio_value = pd.read_json(data_dict.get("positions"))
        self.strategies_returns = pd.read_json(data_dict.get("returns"))
        self.strategies_trades =pd.read_json(data_dict.get("trades"))
        self.strategies_portfolio_value_daily_change =pd.read_json(data_dict.get("portfolio_value"))
        db = myMongo("etf")
        self.etf_descriptions = db.find("etf", "etf_name", "etf_description")
        db.close_connection()

    
    def get_strategies_dfs(self):
        db = myMongo("backtesting")
        self.strategies_description = db.find("strategies_description", "all", None)
        self.strategies_general_stats = db.find("strategies_general_stats", "all", None)
        self.strategies_portfolio_value = db.find("strategies_portfolio_value", "all", None)
        self.strategies_returns = db.find("strategies_returns", "all", None)
        self.strategies_trades = db.find("strategies_trades", "all", None)


        self.strategies_description["id"] = self.strategies_description["strategy_id"].apply(lambda x : float(x.split("S")[-1]))
        self.strategies_description.sort_values("id",inplace=True)
        self.strategies_trades.sort_values("date", inplace=True)
    
        
        db.close_connection()

        db = myMongo("etf")

        self.etf_descriptions = db.find("etf", "etf_name", "etf_description")

        db.close_connection()
        

    def get_strategies_names(self):
        return  {f"{v} - {k}":v for k,v in self.strategies_description[["strategy_name","strategy_id"]].values}

    def get_strategies_details(self, details="description", filter=None, language="en"):
        
        keys = ["strategy_id"]
        
        if details == "description":
            if language == "en":
                keys.extend(["strategy_description"])
            else:
                keys.extend(["strategy_description-cn"])
        elif details == "parameters":
            if language == "en":
                keys.extend(["rebalancing_frequency", "markets", "asset_classes", "period"])
            elif language == "cn":
                keys.extend(["rebalancing_frequency-cn", "markets", "asset_classes-cn", "period"])

        # print(keys)
        df = self.strategies_description[keys]
        
        df = self.strategies_description[keys]
        if filter:
            df = self._filter_df_by_id(df, filter)
        return  df


    def get_strategies_stats(self, filter=None):
        df = self.strategies_general_stats
        if filter:
            df = self._filter_df_by_id(df, filter)
        return df


    def get_strategies_portfolio_value(self, filter=None, daily_change=False):
        if not daily_change: 
            df = self.strategies_portfolio_value
        else:
            df = self.strategies_portfolio_value_daily_change
        
        df.sort_values(by=['date'],inplace=True)
        if not filter is None:
            df = self._filter_df_by_id(df, filter)
            df.sort_values("date", inplace=True)
        return df

    def get_assets_mean_distribution(self, filter=None, top_size=5, as_df = False):
        df = self.strategies_portfolio_value.copy()

        if filter:
            df = self._filter_df_by_id(df, filter)
        
        df.dropna(axis=1, inplace=True)

        df = df[[c for c in df.columns if c not in ["date", "prt_value" , "strategy_id"]]]

        df_sorted = df.mean().sort_values(ascending=False)

        if top_size:
            df = df_sorted[:top_size]
            df["other"] = df_sorted[top_size:].sum()
        else:
            df = df_sorted

        if as_df:
            return pd.DataFrame({"assets": df.index.tolist(), "values":df.values}, index=list(range(len(df.values))))

        return df

    def get_trades(self, filter=None):
        df = self.strategies_trades.copy()

        if filter:
            df = self._filter_df_by_id(df, filter)
        
        df.dropna(axis=1, inplace=True)
        df["date"] = df["date"].dt.date
        df = df[["date", "symbol", "amount", "price", "value"]]

        return df     

    def get_basket_mean_values(self, filter, basket_type="asset_class",top_size=5):

        df = self.strategies_portfolio_value.copy()

        if filter:
            df = self._filter_df_by_id(df, filter)

        df.dropna(axis=1, inplace=True)

        df = df[[c for c in df.columns if c not in ["date", "prt_value" , "strategy_id"]]]
        
        ac_translation = {c:self._get_basket(f"{c}.US_5", basket_type) for c in df.columns if c not in ["_id", "cash", "BITCOIN"]}
        
        new_df = pd.DataFrame()

        for asset_class in set(ac_translation.values()): 
            ac_etfs = [k for k,v in ac_translation.items() if v == asset_class]
            if len(new_df) == 0:
                new_df = pd.DataFrame({asset_class: df[ac_etfs].sum(axis=1, skipna=True).mean()}, index=["mean_values"])
            else:
                new_df[asset_class] = df[ac_etfs].sum(axis=1, skipna=True).mean()

        new_df["cash"] = df[["cash"]].sum(axis=1, skipna=True).mean()
        
        if "BITCOIN" in df.columns:
            new_df["BITCOIN"] = df[["BITCOIN"]].sum(axis=1, skipna=True).mean()

        new_df = new_df.T["mean_values"]

        if basket_type == "asset_class":
            df_sorted = new_df.sort_values(ascending=False)

            df = df_sorted[:top_size]
            
            df["other"] = df_sorted[top_size:].sum()

            new_df = df[df>0.001]

        return new_df      

    def _get_basket(self,ticker, basket_type):
        
        if basket_type == "sector":
            return self.etf_descriptions[self.etf_descriptions["symbol"] == ticker]["sector"].values[0]
        elif basket_type == "asset_class":
            return self.etf_descriptions[self.etf_descriptions["symbol"] == ticker]["Asset Class"].values[0]

 