import requests 

class StrategiesAPI():
    def __init__(self):
        self.strategy = None
        self.params = None
        # self.base_url = "http://127.0.0.1:5000/"
        self.base_url = "https://api-strategies-ibyah76s5q-lz.a.run.app/"
    
    @staticmethod
    def _build_content(strategy_name, assets):
        if type(strategy_name) != str: raise ValueError("Strategy Name has to be a string")
        if type(assets) != list: raise ValueError("Assets have to be a list")
        return {"strategy":strategy_name, "assets":assets}

    def run_strategy(self, strategy_name, assets):
        url = self.base_url + "run_strategy"
        payload = self._build_content(strategy_name, assets)
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            return None

class SimulationsApi():
    def __init__(self, assets, weights, days=20):
        self.assets = assets
        self.weights = weights
        self.days = days
        # self.base_url = "http://127.0.0.1:5000/"
        self.base_url = "https://api-strategies-ibyah76s5q-lz.a.run.app/"
    
    def run_simulation(self):
        url = self.base_url + "run_simulation"
        payload = {"assets":self.assets, "weights":self.weights, "days":self.days} 
        r = requests.post(url, json=payload)
        print(r.status_code)
        if r.status_code == 200:
            return r.json()
        else:
            return None


if __name__ == "__main__":
    s = SimulationsApi(["SPY.US_5"], [1], 20)
    results, returns = s.run_simulation()


