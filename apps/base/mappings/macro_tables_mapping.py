
mapping = {
    "income":{"Disposable Income":"DSPIC96", "Personal Savings":"PSAVERT", "PCE":"PCEC96"},
    "sales" : {"Retail": "RSXFS", "Ecommerce":"ECOMPCTSA", "Industrial Production":"INDPRO", "Vehicles":"TOTALSA"},
    "labor": {"Unemployment Rate":"UNRATE", "Initial Weekly Jobless Claims":"ICSA", "Pandemic Unemployment Assistance":"PUAICPR"},
    "inflation": {"CPI":"CPIAUCSL" , "PPI":"PPIACO"},
    "housing": {"Home Price Index": "CSUSHPINSA" , "Houses Started":"HOUST", "House Prices":"MSPUS", "House Supply":"MSACSR"},
}


def get_tables_mapping(macro_indicator):
    if macro_indicator == "macro_indicators":
        return mapping.keys()
    return mapping.get(macro_indicator, "")