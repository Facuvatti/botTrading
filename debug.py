# -*- coding: utf-8 -*-
import logging
import os
from operate import executeMarket, executeOCO
from decision import positionSize, stopLossPercent, slStopPrice, takeProfitPercent, side
closeOrders = []
countTakeProfit = 0
countStopLoss = 0
win = 0
loss = 0
# Si la tabla de metricas (archivo metrics.json) no existe crearla y agregarle las columnas correspondientes
if not os.path.isfile('metrics.json'):
    with open('metrics.json', 'w') as f:
        f.write('{"countTakeProfit": 0, "countStopLoss": 0, "win": 0, "loss": 0, "profitFactor": 0, "operationsAmount": 0, "Acurrancy": 0, "profitability": 0, "riskRewardRatio": 0, "profitAverage": 0, "lossAverage": 0}')
marketOrder = executeMarket(side, positionSize)
orderTP, orderSL = executeOCO(stopLossPercent, takeProfitPercent, slStopPrice, marketOrder)
while orderTP['status'] != 'filled' and orderSL['status'] != 'filled':
    if orderTP['status'] == 'filled':
        closeOrders.append(orderTP)
        countTakeProfit = countTakeProfit + 1
    elif orderSL['status'] == 'filled':
        closeOrders.append(orderSL)
        countStopLoss = countStopLoss + 1
    for closeOrder in closeOrders:
        startUSDT = marketOrder["price"]*marketOrder["amount"]
        lastUSDT = closeOrder["price"]*closeOrder["amount"]
        if marketOrder["side"] == "BUY":
            result = lastUSDT - startUSDT
        elif marketOrder["side"] == "SELL":
            result = startUSDT - lastUSDT
        
        if result > 0 : # Es profit
            logging.info(f"Gane {result} USDT en la operacion N° {closeOrder['id']}")
            win = win + result
        if result < 0: # Es loss
            logging.info(f"Perdi {result} USDT en la operacion N° {closeOrder['id']}")
            loss = loss + result
    operationsAmount = operationsAmount + 1
profitFactor = abs(win / loss) if loss != 0 else float('inf')
if profitFactor > 1:   
    profitability = "es rentable"  
elif profitFactor == 1:
    profitability = "gana lo mismo que pierde"
elif profitFactor < 1:
    profitability = "no es rentable"

Accurancy = (countTakeProfit/operationsAmount)*100 if operationsAmount > 0 else 0
profitAverage = win / countTakeProfit if countTakeProfit > 0 else 0
lossAverage = abs(loss) / countStopLoss if countStopLoss > 0 else 0
riskRewardRatio = (profitAverage / lossAverage) if lossAverage > 0 else float('inf')
logging.info(f"""
El bot esta vez {profitability} ({profitFactor}) y gano o perdio un total de: {win-loss} USDT
🎯 Precisión (Accuracy): {Accurancy:.2f}%
⚖️ Relación riesgo recompensa: {riskRewardRatio:.2f}
🔁 Cantidad de operaciones: {operationsAmount}

✅ Take Profits alcanzados: {countTakeProfit}
⛔ Stop Losses alcanzados: {countStopLoss}

📈 Ganancia promedio: {profitAverage} USDT
💰 Ganancia total: {win:.2f} USDT

📉 Pérdida promedio: {lossAverage} USDT
😭 Pérdida total: {loss:.2f} USDT
""")
