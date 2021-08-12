import pymongo
from bson.objectid import ObjectId 
from pymongo import MongoClient
import json
import pandas as pd
import datetime
import dns
import os
import sys

from ..cred_utils import get_credentials

class myMongo():
    def __init__(self, db_name):
        self.user = get_credentials('MONGO_USER')
        self.pwd = get_credentials('MONGO_PASSWORD')
        self.cluster_name = get_credentials('MONGO_CLUSTER')
        self.db_name = db_name
        self.cnn_str = f"mongodb+srv://{self.user}:{self.pwd}@{self.cluster_name}/{self.db_name}?retryWrites=true&w=majority"
        print(self.cnn_str)
        self.cluster = MongoClient(self.cnn_str)
        self.db = self.cluster[self.db_name]
    
    def close_connection(self):
        self.cluster.close()
    
    def clean_db(self, collection_name):
        collection = self.db[collection_name]
        results = collection.delete_many({})
        return results.acknowledged       

    def clean_entry(self,collection_name,entry_name, entry_value):
        """
        clean_entry("strategies_description","strategy_id", "S1"):
        """
        collection = self.db[collection_name]
        results = collection.delete_many({entry_name:entry_value})
        return results.acknowledged

    def save_in_db(self, df, collection_name):
        collection = self.db[collection_name]
        for col in df.columns:
            if df[col].dtype == "timedelta64[ns]":
                df[col]=df[col].astype(str)
        res = collection.insert_many(df.to_dict("records"))
        return res
    

    def find(self, collection_name, key, value):
        """
        find_in_db("strategies_description", key="all", value=None)
        
        find_in_db("strategies_description", key="strategy_id", value="S1")
        """

        collection = self.db[collection_name]

        res = pd.DataFrame()

        if key == "all":
            res = pd.DataFrame(list(collection.find({})))
        else:
            res = pd.DataFrame(list(collection.find({key:value})))

        res.reset_index(drop=True, inplace=True)

        return res

    