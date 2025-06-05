from binance.client import Client
import logging
client = Client(api_key='zYDWPJzOj0jVT2a1OQdRlxSc6Y8Z60vbpw9lmz1tpU32U5wGnNXCtdHrkxV9gLIw', api_secret='asJ0B0hqMdI9JEdXqBmz804lN40KNx8dLBcueiKoFos25IBSeQvm3o4i4tLDvbDO')
client.API_URL = "https://testnet.binance.vision/api/v3"
def executeMarket(side:str, positionSize):
    # Estructura de datos de la operación MARKET
    firstOperation = {
    "symbol": "BTCUSDT",
    "side": side.upper(),
    "recvWindow": 1000,
    "neworderrespType": "RESULT",
    "type": "MARKET",
    "computeCommissionRates" : True
    }
    # Agregando datos a la estructura basado en el "lado" de la operación
    if side == "BUY":
        firstOperation["quoteOrderQty"] = positionSize
    if side == "Sell":
        firstOperation["quantity"] = positionSize
    # Ejecutando la operación y obteniendo la orden
    marketOrder = client.new_order(**firstOperation) 
    logging.info(f"First order: {marketOrder} \n")
    # Retornando la orden
    return marketOrder

def executeOCO(stopLossPercent:float, takeProfitPercent:float,slStopPrice:float, marketOrder:dict):
    # Estructura de datos de la operación OCO
    ocoOperation = { 
    "symbol": "BTCUSDT",
    "recvWindow": 1000,
    "neworderrespType": "RESULT",
    "stopPrice": slStopPrice,
    "computeCommissionRates" : True
    } 
    logging.info(f"{marketOrder['side']} \n")
    # Agregando datos a la estructura basado en el "lado" de la operación
    if marketOrder["side"] == "BUY":
        ocoOperation["side"] = "SELL"
        ocoOperation["aboveType"] = "LIMIT_MAKER"
        ocoOperation["belowType"] = "STOP_LOSS_LIMIT"
        ocoOperation["quantity"] = marketOrder["amount"]
        ocoOperation["abovePrice"] = marketOrder["price"]*takeProfitPercent
        ocoOperation["belowPrice"] = marketOrder["price"]*stopLossPercent
    elif marketOrder["side"] == "SELL":
        ocoOperation["side"] = "BUY"
        ocoOperation["aboveType"] = "STOP_LOSS_LIMIT"
        ocoOperation["belowType"] = "LIMIT_MAKER"
        ocoOperation["quoteOrderQty"] = marketOrder["amount"]
        ocoOperation["abovePrice"] = marketOrder["price"]*stopLossPercent
        ocoOperation["belowPrice"] = marketOrder["price"]*takeProfitPercent
    logging.info(f"Operacion OCO: {ocoOperation} \n")
    # Ejecutando la operación y obteniendo la orden
    ocoOrder = client.new_oco_order(**ocoOperation)
    logging.info(f"Orden OCO: {ocoOrder} \n")
    # Separando las ordenes Take Profit y Stop Loss
    if marketOrder["side"] == "BUY":
        orderTP = ocoOrder["orderReports"][0]
        orderSL = ocoOrder["orderReports"][1]
    elif marketOrder["side"] == "SELL":
        orderTP = ocoOrder["orderReports"][1]
        orderSL = ocoOrder["orderReports"][0]
    logging.info(f"Orden Take Profit: {orderTP} \n Orden Stop Loss: {orderSL} \n")
   # Retornando las ordenes
    return orderTP, orderSL, marketOrder
