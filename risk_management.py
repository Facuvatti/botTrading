import pandas as pd
from utils.artificial_inteligence import aiDecides
def adjustRisk(volatility:pd.Series,positionSize:float, stopPrice:float=0.1, takeProfitP:float=0.2, stopLossP:float=None ):
    actualVolatility = volatility[-1]
    tiny = aiDecides(0,1,True)
    big = aiDecides(0,1,True)

    # Puntaje aceptable
    if actualVolatility > 0.5 or (volatility[-2] < 0.5 and actualVolatility == 0.5): 
        positionSize *= tiny

    elif actualVolatility < 0.5 or (volatility[-2] > 0.5 and actualVolatility == 0.5):
        positionSize *= big
    stopPrice *= 1-actualVolatility
    if stopLossP != None:
        stopLossP *= 1-actualVolatility
    takeProfitP *= 1-actualVolatility
    return [positionSize,stopPrice, takeProfitP,stopLossP]


