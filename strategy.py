#from utils.indicators import SignalGenerator
import pandas as pd
import numpy as np
import json
from utils.others import logg_format, aleatory_list # aleatory_list está para debug
import random # Para debug
import logging
from risk_management import adjustRisk  
logg_format()

class weather():
    def __init__(self, ohlcv, data_folder="data_bases"):
        self.ohlcv = ohlcv
        self.data_folder = data_folder
    def volatility(self):
        return aleatory_list(10,0,1,True)
    def slope(self):
        return aleatory_list(10,0,1,True)
    def news(self):
        return float(random.randint(0,1))
    def run(self):
        return self.volatility(), self.slope(), self.news()
class strategy():
    def __init__(self,volatility:pd.Series, slope:pd.Series, news:pd.Series):
        self.volatility = volatility
        self.slope = slope
        self.news = news
    def choose(self):
        self.volatility
        self.slope
        self.news
        # Se usan los valores para decidir qué estrategia usar

        return random.randint(1,5)
    def run(self,index:int):
        if index == 1:
            
            positionSize = random.randint(1,100)
            stopPrice = random.uniform(0,1)
            takeProfitP = random.uniform(0,1)
            stopLossP = random.uniform(0,1)
        adjustedParams = adjustRisk(self.volatility,positionSize,stopPrice,takeProfitP,stopLossP)

        