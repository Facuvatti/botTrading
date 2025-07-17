# -*- coding: utf-8 -*-
import logging
from utils.operate import execute
from risk_management import adjustRisk
from strategy import weather, Ultimate_strategy, export_chart_data
from utils.artificial_inteligence import aiDecides
import fetch_data
from backtesting import Backtest
import pandas as pd
exchange = fetch_data.binance()
fetch_data.ohlcv(exchange,"1m",1000,new=True)
ohlcv = pd.read_csv("static/ohlcv_data.csv")
test = True
if test:

    bt = Backtest(ohlcv,Ultimate_strategy,cash=1000000.0,commission=.002)
    export_chart_data(bt.run())

#orderTP, orderSL, marketOrder = execute.long(positionSize,takeProfitPercent,stopPrice,stopLossPercent)
    