from .custom_libraries.mongo_connections import myMongo


backtesting_strategies = {
    "S1 - Benchmark": "S1",
    "S3 - Institutional holders":"S3",
    "S4 - Deep Learning Best Performers":"S4",
    "S5 - DNN SMA Markowitz Allocation":"S5"
}

class Strategies():
    def __init__(self):
        self.strategies_description = None
        self.strategies_general_stats = None
        self.get_strategies_dfs()
    
    def _filter_df_by_id(self, df, filter):
        if type(filter) != list:
            raise ValueError("Please pass filter as a list")
        df = df[df["strategy_id"].isin(filter)]
        return df
        
    def get_strategies_dfs(self):
        db = myMongo("backtesting")
        self.strategies_description = db.find("strategies_description", "all", None)
        self.strategies_general_stats = db.find("strategies_general_stats", "all", None)
        self.strategies_portfolio_value = db.find("strategies_portfolio_value", "all", None)
        db.close_connection()
        

    def get_strategies_names(self):
        return  {f"{v} - {k}":v for k,v in self.strategies_description[["strategy_name","strategy_id"]].values}

    def get_strategies_details(self, details="description", filter=None):
        
        keys = ["strategy_id"]
        
        if details == "description":
            keys.extend(["strategy_description"])
        elif details == "parameters":
            keys.extend(["rebalancing_frequency", "markets", "asset_classes", "period"])

        df = self.strategies_description[keys]
        
        if filter:
            df = self._filter_df_by_id(df, filter)
        return  df


    def get_strategies_stats(self, filter=None):
        df = self.strategies_general_stats
        if filter:
            df = self._filter_df_by_id(df, filter)
        return df


    def get_strategies_portfolio_value(self, filter):
        df = self.strategies_portfolio_value
        if filter:
            df = self._filter_df_by_id(df, filter)
        
        return df

    def get_assets_mean_distribution(self, filter, top_size=5):
        df = self.strategies_portfolio_value.copy()

        if filter:
            df = self._filter_df_by_id(df, filter)
        
        df.dropna(axis=1, inplace=True)

        df = df[[c for c in df.columns if c not in ["date", "prt_value" , "strategy_id"]]]

        df_sorted = df.mean().sort_values(ascending=False)

        df = df_sorted[:top_size]
        
        df["other"] = df_sorted[top_size:].sum()
        

        return df
            

