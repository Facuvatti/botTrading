# takeProfit y stopLoss ya están definidos porque los generó la estrategia. Tambien el positionSize
from math import sqrt
import pandas as pd
import numpy as np
import random
def aiDecides(x):
    return random.seed(x)
volatility =pd.Series([1,2,3,4,5,6])
positionSize = 10
actualVolatility = volatility[-1]
averageVolatility = volatility.sum()/len(volatility)
standardDeviation = sqrt((volatility.sum()-averageVolatility)**2)
highVolatility = averageVolatility + aiDecides(0) * standardDeviation
mediumVolatility = averageVolatility + aiDecides(1) * standardDeviation
tiny = aiDecides(2)
big = aiDecides(3)
shortRange = aiDecides(4) # Tiene que ser un numero negativo
longRange = aiDecides(5) # Tiene que ser un numero positivo
# Puntaje aceptable
if actualVolatility >= mediumVolatility and actualVolatility < highVolatility: 
    positionSize *= tiny
    
elif actualVolatility >= highVolatility:
    positionSize *= big