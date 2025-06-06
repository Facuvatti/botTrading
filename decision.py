from math import sqrt


# Extrayendo solo los ultimos 10 buyScores
def decide(riskManagement, parameters):
    buyScores = riskManagement["buyScores"]
    sellScores = riskManagement["sellScores"]
    positionSize = riskManagement["positionSize"]
    stopLossPercent = riskManagement["stopLossPercent"]
    slStopPrice = riskManagement["slStopPrice"]
    takeProfitPercent = riskManagement["takeProfitPercent"]
    periods = parameters["periods"]
    shortRange = parameters["shortRange"]
    longRange = parameters["longRange"]
    acceptable = parameters["acceptable"]
    excelent = parameters["excelent"]
    tiny = parameters["tiny"]
    big = parameters["big"]
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

