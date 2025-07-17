from backtesting.test import GOOG
import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover
from backtesting import Backtest

import json
class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 50
    n2 = 200
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1,name=f"sma{self.n1}")
        self.sma2 = self.I(SMA, self.data.Close, self.n2,name=f"sma{self.n2}")
    
    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()



print(GOOG)