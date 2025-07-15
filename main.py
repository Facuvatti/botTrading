# -*- coding: utf-8 -*-
import logging
import os
import json
from utils.operate import execute
from risk_management import adjustRisk
from strategy import weather, strategy
from utils.artificial_inteligence import aiDecides
volatility, slope, news = weather.run()
strategy.run(strategy.choose(volatility,slope,news))

orderTP, orderSL, marketOrder = execute.long(positionSize,takeProfitPercent,stopPrice,stopLossPercent)
    