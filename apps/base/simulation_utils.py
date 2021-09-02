from .api_handler import SimulationsApi
import pandas as pd
import time

class Simulation():
    def __init__(self, assets, weights, days=20):
        self.assets = assets 
        self.weights = weights
        self.days=days
        self.status = None

    @property
    def simulation(self):
        simulation = SimulationsApi(self.assets, self.weights, self.days)
        return simulation.run_simulation() 

    def get_results(self):
        start = time.monotonic()
        r = self.simulation
        print(f'Time taken for simulation: {time.monotonic() - start}')
        if not r is None:
            self.status = 200
            results, returns = pd.read_json(r.get("results")), pd.read_json(r.get("returns"))
            return results, returns
        else:
            self.status = 400
            return None

# assets = ['FXE.US_5'] 
 
# weights = [1]

# assets = ['FXE.US_5','IVE.US_5','SPY.US_5','EMB.US_5','IVV.US_5','GSG.US_5',
# 'JNK.US_5','UDOW.US_5','RSP.US_5','FXA.US_5','COPX.US_5','XHB.US_5',
# 'XLK.US_5','EWU.US_5','EWG.US_5','SPLV.US_5','ECH.US_5','XRT.US_5',
# 'XLP.US_5','SLV.US_5','SVXY.US_5','XLY.US_5','XLV.US_5','XLU.US_5',
# 'RPG.US_5','UPRO.US_5','SOXX.US_5','VNQI.US_5','XOP.US_5','IBB.US_5']

# weights = [0.0629, 0.0405, 0.0395, 0.0348, 0.0323, 0.0322, 0.0285, 0.0278, 0.0241, 0.0235, 0.0227, 0.0215, 0.0199, 0.018500000000000003, 0.0168, 0.016200000000000003, 0.0161, 0.0148, 0.0137, 0.0129, 0.011000000000000001, 0.0089, 0.0086, 0.0085, 0.0077, 0.004699999999999999, 0.0036, 0.0031, 0.0029, 0.0029]

# print(len(assets), len(weights))
# s = Simulation(assets, weights)
# print(s.get_results())

