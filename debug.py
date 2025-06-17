# -*- coding: utf-8 -*-
import logging
import os
import json
from operate import executeMarket, executeOCO
from decision import decide
from scores import riskManagement
from artificial_inteligence import parameters
positionSize, stopLossPercent, slStopPrice, takeProfitPercent, side = decide(riskManagement, parameters)
# Si la tabla de metricas (archivo metrics.json) no existe crearla y agregarle las columnas correspondientes
while positionSize != None and stopLossPercent != None and slStopPrice != None and takeProfitPercent != None and side != None:
    if not os.path.isfile('metrics.json'):
        metrics = {
        "countTakeProfit": 0,
        "countStopLoss": 0,
        "win": 0,
        "loss": 0,
        "profitFactor": 0,
        "operationsAmount": 0,
        "Accurancy": 0,
        "riskRewardRatio": 0,
        "profitAverage": 0,
        "lossAverage": 0
        }
        with open('metrics.json', 'w') as f:
            json.dump(metrics, f, indent=4) 
    with open('metrics.json', 'r') as f:
        metrics = json.load(f)
    marketOrder = executeMarket(side, positionSize)
    orderTP, orderSL = executeOCO(stopLossPercent, takeProfitPercent, slStopPrice, marketOrder)
    while orderTP['status'] != 'filled' and orderSL['status'] != 'filled':
        if orderTP['status'] == 'filled':
            closeOrder = orderTP
            metrics['countTakeProfit'] += 1
        elif orderSL['status'] == 'filled':
            closeOrder = orderSL
            metrics['countStopLoss'] += 1
        startUSDT = marketOrder["price"]*marketOrder["amount"]
        lastUSDT = closeOrder["price"]*closeOrder["amount"]
        if marketOrder["side"] == "BUY":
            result = lastUSDT - startUSDT
        elif marketOrder["side"] == "SELL":
            result = startUSDT - lastUSDT
        
        if result > 0 : # Es profit
            logging.info(f"Gane {result} USDT en la operacion N° {closeOrder['id']}")
            metrics['win'] += result
        if result < 0: # Es loss
            logging.info(f"Perdi {result} USDT en la operacion N° {closeOrder['id']}")
            metrics['loss'] += result
    metrics['profitFactor'] = abs(metrics['win'] / metrics['loss']) if metrics['loss'] != 0 else float('inf')
    if metrics['profitFactor'] > 1:   
        profitability = "es rentable"  
    elif metrics['profitFactor'] == 1:
        profitability = "gana lo mismo que pierde"
    elif metrics['profitFactor'] < 1:
        profitability = "no es rentable"

    with open('metrics.json', "r") as file:
        metrics = json.load(file)
    metrics['operationsAmount'] += 1
    metrics['Accurancy'] = (metrics['countTakeProfit']/metrics['operationsAmount'])*100 if metrics['operationsAmount'] > 0 else 0
    metrics['profitAverage'] = metrics['win'] / metrics['countTakeProfit'] if metrics['countTakeProfit'] > 0 else 0
    metrics['lossAverage'] = abs(metrics['loss']) / metrics['countStopLoss'] if metrics['countStopLoss'] > 0 else 0
    metrics['riskRewardRatio'] = (metrics['profitAverage'] / metrics['lossAverage']) if metrics['lossAverage'] > 0 else float('inf')

    logging.info(f"""
    El bot esta vez {profitability} ({metrics['profitFactor']}) y gano o perdio un total de: {metrics['win']-metrics['loss']} USDT
    🎯 Precisión (Accuracy): {metrics['Accurancy']:.2f}%
    ⚖️ Relación riesgo recompensa: {metrics['riskRewardRatio']:.2f}
    🔁 Cantidad de operaciones: {metrics['operationsAmount']}

    ✅ Take Profits alcanzados: {metrics['countTakeProfit']}
    ⛔ Stop Losses alcanzados: {metrics['countStopLoss']}

    📈 Ganancia promedio: {metrics['profitAverage']} USDT
    💰 Ganancia total: {metrics['win']:.2f} USDT

    📉 Pérdida promedio: {metrics['lossAverage']} USDT
    😭 Pérdida total: {metrics['loss']:.2f} USDT
    """)
