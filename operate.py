from binance.client import Client
import logging
client = Client(api_key='zYDWPJzOj0jVT2a1OQdRlxSc6Y8Z60vbpw9lmz1tpU32U5wGnNXCtdHrkxV9gLIw', api_secret='asJ0B0hqMdI9JEdXqBmz804lN40KNx8dLBcueiKoFos25IBSeQvm3o4i4tLDvbDO')
client.API_URL = "https://testnet.binance.vision/api/v3"
class execute():
    def __init__(self):
        pass
    @staticmethod
    def Market(side:str, positionSize:float):
        # Estructura de datos de la operación MARKET
        Operation = {
        "symbol": "BTCUSDT",
        "side": side.upper(),
        "recvWindow": 1000,
        "neworderrespType": "RESULT",
        "type": "MARKET",
        "computeCommissionRates" : True
        }
        # Agregando datos a la estructura basado en el "lado" de la operación
        if side == "BUY":
            Operation["quoteOrderQty"] = positionSize
        if side == "Sell":
            Operation["quantity"] = positionSize
        # Ejecutando la operación y obteniendo la orden
        marketOrder = client.create_order(**Operation) 
        logging.info(f"market order: \n{marketOrder} \n")
        # Retornando la orden
        return marketOrder
    @staticmethod
    def OCO(takeProfitPercent:float,StopPrice:float, marketOrder:dict,stopLossPercent:float=None):
        # Estructura de datos de la operación OCO
        Operation = { 
        "symbol": "BTCUSDT",
        "recvWindow": 1000,
        "neworderrespType": "RESULT",
        "stopPrice": StopPrice,
        "computeCommissionRates" : True
        } 
        logging.info(f"{marketOrder['side']} \n")
        # Agregando datos a la estructura basado en el "lado" de la operación
        if marketOrder["side"] == "BUY":
            Operation["side"] = "SELL"
            Operation["aboveType"] = "LIMIT_MAKER"
            if stopLossPercent == None:
                Operation["belowType"] = "STOP_LOSS_MARKET"
            else:
                Operation["belowType"] = "STOP_LOSS_LIMIT"
                Operation["belowPrice"] = marketOrder["price"] - marketOrder["price"]*stopLossPercent
            Operation["quantity"] = marketOrder["amount"]
            Operation["abovePrice"] = marketOrder["price"] + marketOrder["price"]*takeProfitPercent
            
        elif marketOrder["side"] == "SELL":
            Operation["side"] = "BUY"
            Operation["aboveType"] = "STOP_LOSS_LIMIT"
            Operation["belowType"] = "LIMIT_MAKER"
            Operation["quoteOrderQty"] = marketOrder["amount"]
            Operation["abovePrice"] = marketOrder["price"] + marketOrder["price"]*stopLossPercent
            Operation["belowPrice"] = marketOrder["price"] - marketOrder["price"]*takeProfitPercent
        logging.info(f"\nOperacion OCO: \n\n {Operation} \n")
        # Ejecutando la operación y obteniendo la orden
        ocoOrder = client.create_oco_order(**Operation)
        logging.info(f"\nOrden OCO: \n\n {ocoOrder} \n")
        # Separando las ordenes Take Profit y Stop Loss
        if marketOrder["side"] == "BUY":
            orderTP = ocoOrder["orderReports"][0]
            orderSL = ocoOrder["orderReports"][1]
        elif marketOrder["side"] == "SELL":
            orderTP = ocoOrder["orderReports"][1]
            orderSL = ocoOrder["orderReports"][0]
        logging.info(f"\nOrden Take Profit: \n\n {orderTP} \n\n Orden Stop Loss: \n\n {orderSL} \n")
    # Retornando las ordenes
        return orderTP, orderSL, ocoOrder, Operation
    def long(self,positionSize:float,takeProfitPercent:float,slStopPrice:float,stopLossPercent:float=None):
        marketOrder = self.Market("BUY",positionSize)
        orderTP, orderSL = self.OCO(takeProfitPercent,slStopPrice,marketOrder,stopLossPercent)
        return marketOrder, orderTP, orderSL

    