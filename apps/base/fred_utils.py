from fred.fred import Fred
import os
import pandas as pd


def env_vars(request):
    return os.environ.get("FRED_KEY")

if os.getenv("USERNAME") == "jorgelameira":
    from .custom_libraries.config import get_credential
    api_key = get_credential("FRED_KEY")
else:
    api_key = env_vars


class FredHandler():
    def __init__(self):
        self.fred = Fred(api_key)

    def search_report(self, keyword):
        rslt = self.fred.search_for_series(keyword)
        if len(rslt)  == 0:
            return rslt
        rslt = rslt[["id", "title", "observation_end", "observation_end", "frequency_short", "units", "seasonal_adjustment_short"]]
        return rslt

    def get_series(self, report_id):
        rslt = self.fred.get_series_value(report_id)
        print(len(rslt))
        rslt = rslt[rslt["value"] != "."]
        rslt["value"] = rslt["value"].astype(float)
        rslt["date"] = pd.to_datetime(rslt["date"])
        return rslt


        

