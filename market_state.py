from indicators import SignalGenerator
import pandas as pd
import numpy as np
import json
from utils import logg_format
import logging
logg_format()

class MarketState:
    def trend_type(self, ohlcv):
        trend = None
        indicators = SignalGenerator.calculate_indicators(ohlcv,{'sma': {'length': 20},'sma': {'length': 50},'sma': {'length': 200}})
        for indicator in indicators :
            pass
        return trend