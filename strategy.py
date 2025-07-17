#from utils.indicators import SignalGenerator
import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover
import numpy as np
import json
from utils.others import logg_format, aleatory_list # aleatory_list está para debug
import random # Para debug
import logging
from risk_management import adjustRisk  
from fetch_data import ohlcv
def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()
def export_chart_data(results, path="static"):

    """
    Export chart data including candles, marks, and indicators to a JSON file.

    This function processes the results from a backtesting strategy, extracting
    relevant data such as candlestick chart data, trade entry and exit markers,
    and various technical indicators. The data is then formatted and exported
    into a JSON file for use in lightweight charting applications.

    Parameters:
    results : object
        The backtesting results object containing strategy data and trades.
    filename : str, optional
        The file path where the JSON data will be saved (default is
        "static/chart_data.json").

    The exported JSON file includes:
    - "candles": A list of candlestick data with time, open, high, low, close,
    and volume information.
    - "marks": Trade entry and exit markers with time, position, color, shape,
    and text annotations.
    - "indicators": A list of indicators with name, type (line or histogram),
    and data points.
    Create an instance (object) of the Backtest class from backtesting library, to test the strategy with the exported data and
    visualize the results in a charting application with this function.
    Like this way: 
    bt = Backtest(
    data: DataFrame,
    strategy: type[Strategy],
    *,
    cash: float = 10000,
    spread: float = 0,
    commission: float | Tuple[float, float] = 0,
    margin: float = 1,
    trade_on_close: bool = False,
    hedging: bool = False,
    exclusive_orders: bool = False,
    finalize_trades: bool = False).run()
    Use .run to get the results of the backtest
    """
    def startswith_any(string, prefixes):
        """
        Verifica si una cadena comienza con alguno de los prefijos en una lista.

        Args:
            cadena: La cadena a verificar.
            lista_prefijos: Una lista de cadenas que podrían ser prefijos.

        Returns:
            True si la cadena comienza con alguno de los prefijos, False en caso contrario.
        """
        return any(string.startswith(prefix) for prefix in prefixes)
    df = results._strategy.data.df.copy()
    trades = results['_trades']
    # Exportar indicadores
    indicators = []

    strategy = results._strategy

    for indicator in strategy._indicators:
        name=indicator.name
        series = indicator
        # Convertimos a lista de puntos para JSON
        arr = []
        for i, val in enumerate(series):
            if pd.isna(val): continue
            ts = int(pd.to_datetime(df.index[i]).timestamp())
            arr.append({ "time": ts, "value": float(val) })
            line_indicators = [
                                "sma",
                                "ema",
                                "wma",
                                "rma", # Media Móvil Suavizada
                                "bbands", # Bandas de Bollinger
                                "rsi",
                                "stoch", # Oscilador Estocástico
                                "macd", # Incluye línea MACD y línea de señal
                                "atr", # Average True Range
                                "cci", # Commodity Channel Index
                                "roc", # Rate of Change
                                "mom", # Momentum
                                "adx", # Average Directional Index (incluye +DI y -DI)
                                "ichimoku", # Ichimoku Kinko Hyo (múltiples líneas)
                                "vwap", # Volume Weighted Average Price
                                "pivot" # Pivot Points
                            ]
            if startswith_any(name, line_indicators):
                itype = "line"
            else:
                itype = "histogram"
        indicators.append({
            "name": name,
            "type": itype,  # podrías usar otro tipo si sabés que es histogram o scatter
            "data": arr
        })
    with open(f"{path}/indicators.json", "w") as f:
        json.dump(indicators, f, indent=2)
    marks = []
    for _, row in trades.iterrows():
        entry_time = df.index[int(row["EntryBar"])]
        exit_time = df.index[int(row["ExitBar"])]

        marks.append({
            "time": int(pd.to_datetime(entry_time).timestamp()),
            "position": "belowBar",
            "color": "blue" if row["Size"] > 0 else "orange",
            "shape": "arrowUp" if row["Size"] > 0 else "arrowDown",
            "text": "Entry Long" if row["Size"] > 0 else "Entry Short"
        })

        marks.append({
            "time": int(pd.to_datetime(exit_time).timestamp()),
            "position": "aboveBar",
            "color": "green" if row["PnL"] >= 0 else "red",
            "shape": "arrowDown" if row["Size"] > 0 else "arrowUp",
            "text": f"Exit ({'Profit' if row['PnL'] >= 0 else 'Loss'})"
        })

    with open(f"{path}/marks.json", "w") as f:
        json.dump(marks, f, indent=2)
    print(f"Datos exportados")
logg_format()

class weather():
    def __init__(self, ohlcv, data_folder="static"):
        self.ohlcv = ohlcv
        self.data_folder = data_folder
    def volatility(self):
        return aleatory_list(10,0,1,True)
    def slope(self):
        return aleatory_list(10,0,1,True)
    def news(self):
        return float(random.randint(0,1))
    def run(self):
        return self.volatility(), self.slope(), self.news()
class Choose():
    def __init__(self,volatility:pd.Series, slope:pd.Series, news:pd.Series):
        self.volatility = volatility
        self.slope = slope
        self.news = news
    def run(self):
        self.volatility
        self.slope
        self.news
        # Se usan los valores para decidir qué estrategia usar

        return random.randint(1,5)
    def run(self,index:int):
        if index == 1:
            
            positionSize = random.randint(1,100)
            stopPrice = random.uniform(0,1)
            takeProfitP = random.uniform(0,1)
            stopLossP = random.uniform(0,1)
       

class Ultimate_strategy(Strategy):

    def init(self,indicators:list=[[SMA,[50]],[SMA,[200]]],positionSize=0.000001):
        # Precompute the two moving averages
        for function,parameters in indicators:
            name = function.__name__ + f"_{parameters[0]}"
            setattr(self,name,self.I(function,self.data.Close,*parameters,name=name))
        self.positionSize = positionSize
    
    def next(self):
        if self.SMA_50 is not None and self.SMA_200 is not None:
            if crossover(self.SMA_50, self.SMA_200):
                self.position.close()
                self.buy(size=self.positionSize)


            elif crossover(self.SMA_200, self.SMA_50):
                self.position.close()
                self.sell()






#adjustedParams = adjustRisk(self.volatility,positionSize,stopPrice,takeProfitP,stopLossP)