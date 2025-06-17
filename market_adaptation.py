from math import sqrt
import logging
from utils import umbral, logg_format
logg_format()
logging.basicConfig(level=logging.DEBUG)
def calculate_correlation_coefficient(x=[], y=[], y_average=[]): # y = btc
    x_average = sum(x) / len(x)
    X = [i - x_average for i in x]
    Y = [i - y_average for i in y]
    numerator = sum([i * j for i, j in zip(X, Y)])
    denominator = sqrt(sum((i-x_average)**2 for i in X) * sum((i-y_average)**2 for i in Y))
    r = numerator / denominator
    corr_change = ((x[-1] - x[-2]) / x[-2]) * 100
    return r, corr_change, x_average

pbi=[]
ipc=[]
unemployement=[]
interest_rate=[]
public_debt=[]
gold=[]
correlations = {
"PBI" : pbi,
"inflation" : ipc,
"unemployement" : unemployement,
"interest rate" : interest_rate,
"public debt" : public_debt,
"gold" : gold
}
btc = []
coeficentes = {}
corr_changes = []
slopes = []
btc_average = sum(btc) / len(btc)
for key, x in correlations:
    coeficentes[key], corr_change, x_average = calculate_correlation_coefficient(x, btc, btc_average)
    slope = coeficentes[key] * x_average
    slopes.append(slope)
    b = [(coeficentes[key] * i) for i in x]
    corr_changes[key] = corr_change
a = btc_average - sum(slopes) # Valor base del activo y cuando el valor de x es cero. 
logging.info(f"Intercepto (a) : {a} \n Cambios de precio de las correlaciónes: {corr_changes} \n Pendiente de las correlaciones: {slopes} \n ")  # Esto solo sirve para verificar que tanto del precio de bitcoin es afectado por estas correlaciones
btc_change = a + sum(b)
logging.info(f"Coeficentes de las correlaciones: {coeficentes} \n Precio promedio del Bitcoin: {btc_average} \n Cambio de precio del Bitcoin influenciado por las correlaciones: {btc_change} y el cambio total: {((btc[-1] - btc[-2]) / btc[-2]) * 100} \n ")
