from math import sqrt
buyScores = [100, 80, 50, 60, 70, 90, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 10, 20, 30, 40] 
sellScores = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10] #Tiene que ser lo contrario de buyScores
positionSize = 0.00001 
stopLossPercent = 0.1
slStopPrice = stopLossPercent-(stopLossPercent*0.1)
takeProfitPercent = 0.1 
# Diccionario con todos los valores, encontrar un buen nombre para el diccionario
riskManagement = {
    "buyScores": buyScores,
    "sellScores": sellScores,
    "positionSize": positionSize,
    "stopLossPercent": stopLossPercent,
    "slStopPrice": slStopPrice,
    "takeProfitPercent": takeProfitPercent
}
# Extrayendo solo los ultimos 10 buyScores
def adjustRisk(parameters):
    buyScores = riskManagement["buyScores"] # Es una lista
    sellScores = riskManagement["sellScores"] # Es una lista
    positionSize = riskManagement["positionSize"] # Es un int
    stopLossPercent = riskManagement["stopLossPercent"] # Es un float 
    slStopPrice = riskManagement["slStopPrice"] # Es un float
    takeProfitPercent = riskManagement["takeProfitPercent"] # Es un float
    periods = parameters["periods"] # Es un int
    shortRange = parameters["shortRange"] # Es un float
    longRange = parameters["longRange"] # Es un float
    acceptable = parameters["acceptable"] # Es un float
    excelent = parameters["excelent"] # Es un float
    tiny = parameters["tiny"] # Es un float
    big = parameters["big"] # Es un float
    scoreAverage = buyScores[-periods:]/periods
    standartDeviation = sqrt((buyScores[-periods:]-scoreAverage)**2)
    acceptableTreshold = scoreAverage + acceptable*standartDeviation
    excelentTreshold = scoreAverage + excelent*standartDeviation
    if buyScores[-1] >= acceptableTreshold[-1] and sellScores[-1] >= acceptableTreshold[-1]:
        raise Exception("No se puede comprar y vender en el mismo momento")
    elif buyScores[-1] >= acceptableTreshold[-1] and not (sellScores[-1] >= acceptableTreshold[-1]):
        side = "BUY"
    elif not (buyScores[-1] >= acceptableTreshold[-1]) and sellScores[-1] >= acceptableTreshold[-1]:
        side = "SELL"
    if (buyScores[-1] > acceptableTreshold[-1] and buyScores[-1] < excelentTreshold[-1]) or (sellScores[-1] > acceptableTreshold[-1] and sellScores[-1] < excelentTreshold[-1]):
        positionSize -= positionSize*tiny
        stopLossPercent -= stopLossPercent*shortRange
        slStopPrice -= slStopPrice*shortRange
        takeProfitPercent -= takeProfitPercent*shortRange
        return positionSize, stopLossPercent, slStopPrice, takeProfitPercent, side
    elif buyScores[-1] > excelentTreshold[-1] or sellScores[-1] > excelentTreshold[-1]:
        positionSize += positionSize*big
        stopLossPercent += stopLossPercent*longRange
        slStopPrice += slStopPrice*longRange
        takeProfitPercent += takeProfitPercent*longRange
        return positionSize, stopLossPercent, slStopPrice, takeProfitPercent, side
    if buyScores[-1] < acceptableTreshold[-1] and sellScores[-1] < acceptableTreshold[-1]:
        print(f"Las señales no estan seguras de operar (puntajes bajos en ambos lados) \n buy: {buyScores[-1]} sell: {sellScores[-1]} \n") 
        return None, None, None, None, None

