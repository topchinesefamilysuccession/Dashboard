from fred.fred import Fred
import os
import pandas as pd



if os.getenv("USERNAME") == "jorgelameira":
    from .custom_libraries.config import get_credential
    api_key = get_credential("FRED_KEY")
else:
    api_key = "2d226d1ec2984e70a665086166231b68"


class FredHandler():
    def __init__(self):
        self.fred = Fred(api_key)

    def search_report(self, keyword, output_only_description=False):
        rslt = self.fred.search_for_series(keyword)
        if len(rslt)  == 0:
            return rslt
        if output_only_description:
            return rslt["notes"]
        return rslt

    def get_series(self, report_id):
        rslt = self.fred.get_series_value(report_id)

        if len(rslt) > 0:
            rslt = rslt[rslt["value"] != "."]
            rslt["value"] = rslt["value"].astype(float)
            rslt["date"] = pd.to_datetime(rslt["date"])
            return rslt
        return []

        

