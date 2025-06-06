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