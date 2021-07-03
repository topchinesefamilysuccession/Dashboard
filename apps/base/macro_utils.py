from .mappings.macro_tables_mapping import get_tables_mapping
from .fred_utils import FredHandler
import pandas as pd
import datetime

class MacroTable():
    def __init__(self, macro_indicator):
        self.macro_indicator = macro_indicator
        self.fred = FredHandler()
        self.reports = {}
        
    def _get_macro_mapping(self):
        return get_tables_mapping(self.macro_indicator)
    
    def _print_reports(self):
        print(self.reports)

    def _get_previous_periods(self, df, period):
        if period[0] == "Y":
            num_years = int(period[1:])
            previous_period = df.tail(1)["date"] - pd.offsets.DateOffset(years=num_years)
        
        if period[0] == "M":
            num_months = int(period[1:])
            previous_period = df.tail(1)["date"] - pd.offsets.DateOffset(months=num_months)
        previous_period_date = previous_period.values[0]
        rslt = df[df["date"]==previous_period_date]


        return rslt

    def _treat_df(self, key, df):

        if key == "current":
            return {"date": df.tail(1)["date"].dt.strftime("%Y-%m-%d").values[0], "value": df.tail(1)["value"].values[0]}
        
        if key == "previous":
            return {"date": df.tail(2)["date"].dt.strftime("%Y-%m-%d").values[0], "value": df.tail(2)["value"].values[0]}

        if key [0]== "Y":
            rslt = self._get_previous_periods(df, key)
            if len(rslt) == 0:
                return {} 
            return {"date": rslt["date"].dt.strftime("%Y-%m-%d").values[0], "value": rslt["value"].values[0]}
        
        if key [0]== "M":
            rslt = self._get_previous_periods(df, key)
            if len(rslt) == 0:
                return {} 
            return {"date": rslt["date"].dt.strftime("%Y-%m-%d").values[0], "value": rslt["value"].values[0]}
        

    def load_reports(self):
        report_keys = self._get_macro_mapping()
        for report_name, report_id in report_keys.items():
            series = self.fred.get_series(report_id)
            if len(series) > 0:
                self.reports.update({report_name:series})
    
    def get_measure_from_reports(self, measure_key="last"):
        if len(self.reports) == 0:
            print("No report found !! Load the reports first !!")
            return []
        measures = {}
        placeholder = pd.DataFrame()
        additional_details_df = pd.DataFrame()
        counter = 0
        for report_name, df in self.reports.items():
            if measure_key == "all":
                dict_keys = {"report":report_name}
                additional_details = {"report":report_name}
                for key in ["current", "previous", "Y1", "Y2"]:
                    rslt = self._treat_df(key, df)
                    if len(rslt) > 0:
                        dict_keys.update({key:rslt.get("value")})
                        additional_details.update({key:rslt.get("date")})
                if len(placeholder) == 0:
                    placeholder = pd.DataFrame(dict_keys,  index=[counter])
                    additional_details_df = pd.DataFrame(additional_details,  index=[counter])
                else:
                    placeholder = placeholder.append(pd.DataFrame(dict_keys,  index=[counter]))
                    additional_details_df = additional_details_df.append(pd.DataFrame(additional_details,  index=[counter]))
                measures = placeholder
            else:
                rslt = self._treat_df(measure_key, df)
                if len(rslt) > 0:
                    measures.update({report_name:rslt})
            counter += 1
        return measures, additional_details_df


        


if __name__ == "__main__":
    macro = MacroTable("inflation")
    macro.load_reports()
    reports = macro.get_measure_from_reports("all")
    print(reports)