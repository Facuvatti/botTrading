import pandas as pd
import pandas_ta as ta
import logging
from utils.others import logg_format
import os
logg_format()
def boundary_signals(close_price = pd.Series, lower_bound = pd.Series, upper_bound = pd.Series, buy_condition='below', sell_condition='above'):
    """
    Retorna señales de compra y venta basadas en límites.
    - buy_condition: 'below' para comprar si el precio está por debajo del límite inferior,
                     'above' para comprar si está por encima.
    - sell_condition: 'above' para vender si el precio está por encima del límite superior,
                      'below' para vender si está por debajo.
    """
    debug_data = pd.DataFrame({
    'Precio Cierre': close_price,
    'Límite Inferior': lower_bound,
    'Límite Superior': upper_bound})
    if buy_condition == 'below':
        buy_signals = (close_price < lower_bound) & lower_bound.notna()
    elif buy_condition == 'above':
        buy_signals = (close_price > lower_bound) & lower_bound.notna()
    if sell_condition == 'above':
        sell_signals = (close_price > upper_bound) & upper_bound.notna() 
    elif sell_condition == 'below':
        sell_signals = (close_price < upper_bound) & upper_bound.notna()  
    else:
        raise ValueError("Condición de compra o venta no reconocida. Debe ser 'below' o 'above'.")
    logging.info(f"Debugg dataframe: \n {debug_data}")
    return buy_signals, sell_signals

class SignalGenerator:
    """Genera señales basadas en scores de indicadores"""
    
    def __init__(self, ohlcv, selected_indicators, data_folder="static"):
        self.ohlcv = ohlcv
        self.data_folder = data_folder
        calculated_indicators = self.calculate_indicators(self.ohlcv, selected_indicators)
        self.buy_signals, self.sell_signals = self.generate_signals(calculated_indicators)

    def calculate_indicators(self, ohlcv: pd.DataFrame, selected_indicators: dict): # selected_indicators es un diccionario con los indicadores y sus parametros, como valor

        calculated_indicators = {}  # Diccionario para almacenar los indicadores calculados
        indicators = selected_indicators.keys()
        if len(selected_indicators) == 1:
            calculation = getattr(ohlcv.ta, indicators[0])(selected_indicators[indicators[0]])
            calculation = calculation.dropna()
            calculated_indicators = calculation
        elif selected_indicators != {}:
            for indicator in indicators:
                try:
                    calculation = getattr(ohlcv.ta, indicator)(selected_indicators[indicator])
                    calculation = calculation.dropna()
                    for i in selected_indicators[indicator]:
                        indicator = indicator + f"_{selected_indicators[indicator][i]}"
                    
                    calculated_indicators[indicator] = calculation

                    logging.info(f"Indicador calculado: {indicator}")
                except AttributeError:
                    logging.error(f"Indicador no encontrado: {indicator}")
                except Exception as e:
                    logging.error(f"Error al calcular el indicador {indicator}: {e}")
            logging.info(f"Estos son los indicadores calculados")
        else:
            logging.info("No se seleccionaron indicadores")
        return calculated_indicators

       
    def generate_signals(self, calculated_indicators):
        try:
            data_folder = self.data_folder
            buy_signals = {}
            sell_signals = {}

            for indicator in calculated_indicators:
                indicator_value = calculated_indicators[indicator]
                logging.info(f"Generando señales para el indicador: {indicator}")   
                # Bollinger Bands
                if indicator == "bbands":
                    logging.info(f"Estos son los valores de las bandas de Bollinger: \n {indicator_value}")
                    lower_band = indicator_value.filter(like="BBL").iloc[:, 0].reindex(self.ohlcv.index)  # Encuentra la columna de la banda inferior
                    upper_band = indicator_value.filter(like="BBU").iloc[:, 0].reindex(self.ohlcv.index)  # Encuentra la columna de la banda superior
                    close_price = self.ohlcv["close"]
                    buy_indicator_signals, sell_indicator_signals = boundary_signals(close_price, lower_band, upper_band, buy_condition='below', sell_condition='above')
                elif indicator in ['sma', 'ema', 'dema', 'tema', 'trima', 'wma', 'zlma', 'vidya', 'kama', 'hma','vwap','coppock','obv']:
                    logging.info(f"Estos son los valores del indicador {indicator}: \n {indicator_value}")
                    buy_indicator_signals = (self.ohlcv['close'] > indicator_value) & indicator_value.notna()
                    sell_indicator_signals = (self.ohlcv['close'] < indicator_value) & indicator_value.notna()
                elif indicator in ['trix', 'dpo','roc']:
                    logging.info(f"Estos son los valores del indicador {indicator}: \n {indicator_value}")
                    buy_indicator_signals = (indicator_value > 0) & indicator_value.notna()
                    sell_indicator_signals = (indicator_value < 0) & indicator_value.notna()
                elif indicator == 'ichimoku':
                    logging.info(f"Estos son los valores del indicador {indicator}: \n {indicator_value}")
                    cloud_upper = indicator_value['Senkou Span A'].reindex(self.ohlcv.index)
                    cloud_lower = indicator_value['Senkou Span B'].reindex(self.ohlcv.index)
                    close_price = self.ohlcv["close"]

                    buy_indicator_signals = (close_price > cloud_upper) & cloud_upper.notna()
                    sell_indicator_signals = (close_price < cloud_lower) & cloud_lower.notna()

                # RSI - Relative Strength Index (Sobrecompra/Sobreventa)
                elif indicator == 'rsi':
                    buy_indicator_signals = (indicator_value < 30) & indicator_value.notna() # Compra si RSI < 30 (sobreventa)
                    sell_indicator_signals = (indicator_value > 70) & indicator_value.notna() # Venta si RSI > 70 (sobrecompra)

                # MFI - Money Flow Index (Similar al RSI pero con volumen)
                elif indicator == 'mfi':
                    buy_indicator_signals = (indicator_value < 20) & indicator_value.notna() # Compra si MFI < 20
                    sell_indicator_signals = (indicator_value > 80) & indicator_value.notna() # Venta si MFI > 80

                # MACD - Moving Average Convergence Divergence
                elif indicator == 'macd':
                    macd_line = indicator_value.filter(like="MACD_").iloc[:, 0].reindex(self.ohlcv.index) #indicator_value.filter(like="MACD_").iloc[:, 0].reindex(self.ohlcv.index)
                    signal_line = indicator_value.filter(like="MACDs_").iloc[:, 0].reindex(self.ohlcv.index)

                    buy_indicator_signals = (macd_line > signal_line) & macd_line.notna() & signal_line.notna() # Compra cuando MACD cruza por encima de la señal
                    sell_indicator_signals = (macd_line < signal_line) & macd_line.notna() & signal_line.notna() # Venta cuando MACD cruza por debajo de la señal

                # CCI - Commodity Channel Index
                elif indicator == 'cci':
                    buy_indicator_signals = (indicator_value < -100) & indicator_value.notna()  # Compra si CCI < -100 (sobreventa)
                    sell_indicator_signals = (indicator_value > 100) & indicator_value.notna()  # Venta si CCI > 100 (sobrecompra)

                # ADX - Average Directional Index (Para medir la fuerza de la tendencia)
                elif indicator == 'adx':
                    if {'ADX_14', 'DIP_14', 'DIN_14'}.issubset(indicator_value.columns):
                        adx_value = indicator_value['ADX_14'].reindex(self.ohlcv.index)
                        di_plus = indicator_value['DIP_14'].reindex(self.ohlcv.index)
                        di_minus = indicator_value['DIN_14'].reindex(self.ohlcv.index)

                        buy_indicator_signals = (adx_value > 25) & (di_plus > di_minus)  # Confirmación de tendencia alcista
                        sell_indicator_signals = (adx_value > 25) & (di_plus < di_minus)  # Confirmación de tendencia bajista
                    else:
                        buy_indicator_signals = sell_indicator_signals = pd.Series(False, index=self.ohlcv.index)
                # Aroon (Aroon Up & Aroon Down)
                elif indicator == 'aroon':
                    aroon_up = indicator_value.filter(like="AROONU_").iloc[:, 0].reindex(self.ohlcv.index)
                    aroon_down = indicator_value.filter(like='AROOND_').iloc[:, 0].reindex(self.ohlcv.index)

                    buy_indicator_signals = (aroon_up > 70) & (aroon_down < 30) & aroon_up.notna() & aroon_down.notna()
                    sell_indicator_signals = (aroon_down > 70) & (aroon_up < 30) & aroon_up.notna() & aroon_down.notna()

                # Supertrend (Indicador de tendencia)
                elif indicator == 'supertrend':
                    supert = indicator_value.filter(like='SUPERT_').iloc[:, 0]
                    buy_indicator_signals = (supert < self.ohlcv['close']) & indicator_value.notna() #.filter(like='AROOND_25').iloc[:, 0]
                    sell_indicator_signals = (supert > self.ohlcv['close']) & indicator_value.notna()

                # Williams %R (Momentum)
                elif indicator == 'willr':
                    buy_indicator_signals = (indicator_value < -80) & indicator_value.notna()  # Compra si %R está en sobreventa
                    sell_indicator_signals = (indicator_value > -20) & indicator_value.notna()  # Venta si %R está en sobrecompra
                # PPO - Percentage Price Oscillator (Similar a MACD)
                elif indicator == 'ppo':
                    ppo_line = indicator_value['PPO_12_26_9'].reindex(self.ohlcv.index)
                    signal_line = indicator_value['PPOs_12_26_9'].reindex(self.ohlcv.index)

                    buy_indicator_signals = (ppo_line > signal_line) & ppo_line.notna() & signal_line.notna() # Compra cuando PPO cruza por encima de la señal
                    sell_indicator_signals = (ppo_line < signal_line) & ppo_line.notna() & signal_line.notna()  # Venta cuando PPO cruza por debajo de la señal
                
                elif indicator == 'kc':
                    # Keltner Channels: Se asume que los datos contienen las claves "KCL_20_2.0" y "KCU_20_2.0"
                    lower_channel = indicator_value["KCL_20_2.0"].reindex(self.ohlcv.index)
                    upper_channel = indicator_value["KCU_20_2.0"].reindex(self.ohlcv.index)
                    close_price = self.ohlcv["close"]
                    buy_indicator_signals, sell_indicator_signals = boundary_signals(close_price, lower_channel, upper_channel)

                elif indicator == 'donchian':
                    # Donchian Channels: Se asume que los datos contienen las claves "Donchian_Lower" y "Donchian_Upper"
                    lower_donchian = indicator_value["Donchian_Lower"].reindex(self.ohlcv.index)
                    upper_donchian = indicator_value["Donchian_Upper"].reindex(self.ohlcv.index)
                    close_price = self.ohlcv["close"]
                    # Estrategia breakout: comprar si el precio rompe por encima de la banda superior,
                    # y vender si rompe por debajo de la banda inferior.
                    buy_indicator_signals, sell_indicator_signals = boundary_signals(close_price, lower_donchian, upper_donchian, buy_condition='above', sell_condition='below')

                elif indicator == 'massi':
                    # Mass Index: Ejemplo de umbrales, comprar cuando cae por debajo de 26.5 y vender cuando sube por encima de 27.
                    buy_indicator_signals = (indicator_value < 26.5) & indicator_value.notna()
                    sell_indicator_signals = (indicator_value > 27) & indicator_value.notna()

                elif indicator == 'chaikin':
                    # Chaikin Volatility: Usamos una media móvil para establecer un umbral simple.
                    avg_chaikin = indicator_value.rolling(window=20).mean()
                    buy_indicator_signals = (indicator_value < avg_chaikin) & indicator_value.notna()
                    sell_indicator_signals = (indicator_value > avg_chaikin) & indicator_value.notna()

                # Default: Promedio del indicador como referencia
                else:
                    average = indicator_value.mean() 
                    buy_indicator_signals = (indicator_value > average) & indicator_value.notna()
                    sell_indicator_signals = (indicator_value < average) & indicator_value.notna()
                
                # Convertir las Series de pandas a listas de booleanos
                buy_indicator_signals = buy_indicator_signals.tolist()
                logging.info(f"Señales de compra en lista, para {indicator}: \n{buy_indicator_signals}")
                sell_indicator_signals = sell_indicator_signals.tolist()
                logging.info(f"Señales de venta en lista, para {indicator}: \n{sell_indicator_signals}")
                buy_signals[indicator] = buy_indicator_signals
                sell_signals[indicator] = sell_indicator_signals
            buy_signals_table = pd.DataFrame(buy_signals)
            sell_signals_table = pd.DataFrame(sell_signals)
            buy_signals_table.to_json(f"{data_folder}/buy_signals.json", indent=4)
            sell_signals_table.to_json(f"{data_folder}/sell_signals.json", indent=4)
            logging.info("Se generaron las señales y fueron guardadas exitosamente")
            return buy_signals, sell_signals
        except Exception as e:
            logging.error(f"Hubo un error en la generación de señales: {e}")

def make_json(self, data_folder=None):
    try:
        if data_folder is None:
            data_folder = self.data_folder
        operation_conditions = pd.read_json(f"{data_folder}/operation_conditions.json")
        buy_signals = pd.read_json("{data_folder}/buy_signals.json")
        sell_signals = pd.read_json("{data_folder}/sell_signals.json")
        buy_signals['Compro'] = operation_conditions['Compra'] # Debugg, para comprobar si las condiciones se calcularon correctamente
        sell_signals['Vendio'] = operation_conditions['Venta'] # Debugg, para comprobar si las condiciones se calcularon correctamente
            

        ruta_archivo = f'{data_folder}/operation_conditions.json' 
        archivo = os.path.basename(ruta_archivo)
   
        os.remove(ruta_archivo)
        logging.info(f'El archivo "{archivo}" ha sido eliminado correctamente.')
        buy_signals.to_json(f"{data_folder}/buy_signals.json")
        sell_signals.to_json(f"{data_folder}/sell_signals.json")
    except FileNotFoundError:
        logging.error(f'El archivo "{archivo}" no existe.')
    except Exception as e:
        logging.error(f'Ocurrió un error al fusionar los archivos json: \n {e}')


