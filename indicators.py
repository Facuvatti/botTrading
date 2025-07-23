import pandas as pd
import pandas_ta as ta
import logging, colorlog
import inspect
def visible_functions(module):
    return [name for name, obj in inspect.getmembers(module) if inspect.isfunction(obj) and obj.__module__ == module.__name__]
def logg_format():
    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red'
    }

    formatter = colorlog.ColoredFormatter(
        "| %(filename)s / %(funcName)s | L %(lineno)d | %(log_color)s%(levelname)-8s%(reset)s: %(message)s",
        log_colors=log_colors
    )

    logger = logging.getLogger()

    # Evita agregar múltiples handlers al logger
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)  # Cambiar según necesidad
def handle_param(parameters,name,value=None,ind_aux=0):
    """
    ----------
    parameters : dict
        Diccionario de parámetros que ingresó el usuario para ajustar cuando quiere que se activen las señales
    name : str
        Nombre del parámetro. Ejemplos: "fast", "slow", "upper", "lower", "threshold" y "activator"
    value : pd.DataFrame/pd.Series
        DataFrame que se va a utilizar para obtener el valor del parámetro.
    ind_aux : int
        Es la posición que se va a usar por defecto, en caso de que value sea un DataFrame. 
        Porque esa posición sería en la que generalmente está el indicador que se va a usar.
        
    Returns
    -------
    Dependiendo de la situación devuelve con el tipo de dato: int, str, pd.Series o None
    Lo que da es justamente el valor que se pretende usar en la función que obtiene las señales.
    
    Maneja un parámetro de un diccionario de parámetros.
    
    Primero verifica si el parámetro existe en el diccionario de parámetros. Si no existe, devuelve None y lanza un error.
    
    Si el parámetro existe, verifica si es un entero, una cadena o una serie de pandas. Si es un entero, lo devuelve tal como es. 
    Si es una cadena, verifica si es un dígito. Si lo es, lo convierte a entero y devuelve el valor correspondiente en la columna de un DataFrame dado como parámetro. 
    Si no es un dígito, devuelve la columna del DataFrame con el nombre de la cadena. 
    Si el parámetro es una serie de pandas, la devuelve tal como es.
    
    Si el parámetro no es ninguno de los casos anteriores, devuelve None y lanza un error.
    
    args

    """

    if name not in parameters:
        logging.error(f"El parámetro '{name}' no se encuentra en el diccionario de parámetros.\n")
        return None
    parameter = parameters[name]
    if parameter is not None:
        if type(parameter) == int:
            param = parameter
        elif type(parameter) == str:    
            if parameter.isdigit():
                parameter = int(parameter) 
                param = value.iloc[:,parameter] if value is not None else None
            else:
                if type(value) == pd.DataFrame:
                    param = value[parameter]
        elif type(parameter) == pd.Series:
            param = parameter
        else:
            if value is not None:
                if type(value) == pd.DataFrame:
                    param = value.iloc[:,ind_aux]
                else:
                    param = value
            else:
                param = None
                raise Warning("No se pudo encontrar el valor del parametro, por lo que se va a considerar vacio.\n")        
        return param
    else:
        logging.error(f"En el diccionario de parametros no se encuentra el parametro '{name}'\n")
def handle_exceptions(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Error en la función {func.__name__}({', '.join(map(repr, args)), ', '.join(f'{k}={v}' for k, v in kwargs.items())}):\n\b{e}\n")
        return None
logg_format()
class Signals:
    def __init__(self):
        pass
    def selector(type_signal:str,params):
        if type_signal == "cruce":
            return Signals.cross(*params)
        elif type_signal == "umbral":
            return Signals.threshold(*params)
        elif type_signal == "adx":
            return Signals.adx(*params)
        elif type_signal == "supertrend":
            return Signals.supertrend(*params)
        else:
            raise Exception("Tipo de señal no reconocido")
    def threshold(activator:pd.Series, lower:int, upper:int) -> pd.Series:
        signals = pd.Series(0, index=activator.index, dtype=int)
        if lower is not None:
            signals = signals + (activator < lower).astype(int)
        if upper is not None:
            signals = signals - (activator > upper).astype(int)
        return signals
    def cross(fast: pd.Series, slow: pd.Series) -> pd.Series:
        """
        Devuelve una señal booleana donde la línea rápida cruza por encima de la lenta si long es True. 
        En caso contrario, cruza por debajo.
        """
        signals = +((fast > slow) & (fast.shift(1) <= slow.shift(1))).astype(int)
        signals -= ((fast < slow) & (fast.shift(1) >= slow.shift(1))).astype(int)
        return  signals


    def adx(adx_col: pd.Series, plusDI: pd.Series, minusDI: pd.Series, threshold: float = 25) -> pd.Series:
        """
        Señal de tendencia fuerte cuando ADX > umbral y +DI cruza -DI.
        """
        return (adx_col > threshold) & (plusDI > minusDI) & (plusDI.shift(1) <= minusDI.shift(1))


    def supertrend(price: pd.Series, supertrend_col: pd.Series) -> pd.Series:
        """
        Señal cuando el precio cruza el supertrend.
        """
        return (price > supertrend_col) & (price.shift(1) <= supertrend_col.shift(1))
class IndicatorsWeather:
    """Devuelve para cada vela del dataframe, un valor numerico de cada elemento climatico segun los indicadores"""
    
    def __init__(self, ohlcv):
        self.ohlcv = ohlcv

    def calculate_indicators(self,indicators:dict): # selected_indicators es un diccionario con los indicadores y sus parametros, como valor

        """
        Calcula los indicadores tecnicos y los devuelve en un diccionario.
        indicators : Diccionario con el formato {indicador: [param1, param2, param3]} donde indicador es un string con el nombre del indicador y param1, param2, param3 son una lista con sus parametros
        Si la key del diccionario es una tupla, se calculan varios indicadores combinados, formato {(indicador1,indicador2): [[param1, param2, param3],[param1, param2, param3]]}
        Devuelve un diccionario con los indicadores ya calculados. Si son combinados, se devuelve un dataframe con cada indicador como una columna.
        """
        ohlcv = self.ohlcv
        calculated_indicators = {}  # Diccionario para almacenar los indicadores calculados
        make_indicators = ta.AnalysisIndicators(ohlcv)
        kwargs = {"close":ohlcv["close"],"high":ohlcv["high"],"low":ohlcv["low"],"open":ohlcv["open"],"volume":ohlcv["volume"]}
        for indicator,params in indicators.items():
            try:
                if isinstance(indicator, tuple) and len(indicator) >= 2:
                    combined = pd.DataFrame()
                    name = ""
                    for ind, param in zip(indicator, params):
                        if isinstance(param, list):
                            add = param[1]
                        elif isinstance(param, dict):
                            add = param["length"]
                        add = str(add)
                        kind = ind + add

                        name = name +"-"+ ind[:3] + add if name != "" else ind[:3] + add
                        if isinstance(param, list):
                            param.update(kwargs)
                            calculation = getattr(make_indicators, ind)(*param, kind=kind)
                        elif isinstance(param, dict):
                            calculation = getattr(make_indicators, ind)(**param, kind=kind)
                        calculation = calculation
                        combined[kind] = calculation
                    calculated_indicators[name] = combined.dropna()
                    continue
                if isinstance(param, list):
                    calculation = getattr(make_indicators, indicator)(*params)
                elif isinstance(param, dict):
                    params.update(kwargs)
                    calculation = getattr(make_indicators, indicator)(**params)
                calculation = calculation
                calculated_indicators[indicator] = calculation.dropna()
                calculated_indicators = calculated_indicators
            except Exception as e:
                logging.error(f"Error al calcular el indicador {indicator}\n{e}")
        

        return calculated_indicators
    def generate_signals(self, calculated_indicators:dict,weights:list,types:list,parameters:list):
        """
        Genera señales de compra y venta basadas en los indicadores calculados.
        - calculated_indicators: Diccionario con los indicadores ya calculados.
        - weights: Lista con los pesos a asignar a cada indicador.
        - types: Lista con los tipos de señal a generar para cada indicador.
        - parameters: Lista de diccionarios con los parámetros para cada indicador.
        
        Devuelve un Series con las señales generadas.
        """

        if len(calculated_indicators) == len(weights) and len(types) == len(weights) and len(parameters) == len(weights):

            ohlcv = self.ohlcv
            close = ohlcv["close"]
            signals = pd.Series(0, index=ohlcv.index, dtype=float)
            debug = pd.DataFrame()
            for (indicator, value), weight, t, params in zip(calculated_indicators.items(), weights, types, parameters):                
                if t == "cruce":
                    fast = handle_param(params,"fast",value)
                    slow = handle_param(params,"slow",value,1)
                    param = [fast, slow] # Cada parametro es una lista con los indicadores a cruzar porque ese indicador es uno combinado que se hizo con varias medias moviles
                elif t == "umbral":
                    upper = handle_param(params,"upper",value)
                    lower = handle_param(params,"lower",value,1)
                    activator = handle_param(params,"activator",close)
                    param = [activator,lower,upper]
                elif t == "adx":
                    param = [value[0], value[1], value[2], handle_param(params,"threshold")]
                elif t == "supertrend":
                    price = handle_param(params, "price", value)
                    supertrend_col = handle_param(params, "supertrend_col", value, 1)
                    param = [price, supertrend_col]
                else:
                    raise ValueError(f"Tipo de señal no reconocido: {t}")
                signal = Signals.selector(t,param)
                signal = signal.fillna(0)
                debug = pd.concat([debug, value], axis=1)
                debug[f"signal_{indicator[:3]}"] = signal
                signals += signal *weight
            debug["SIGNALS"] = signals
            signals = signals.fillna(0)
            return signals, debug.dropna()

        else:
            raise ValueError(f"Los pesos, tipos y parametros deben tener la misma longitud que los indicadores calculados\n \
                Peso: {len(weights)}\n \
                Tipos: {len(types)}\n \
                Parametros: {len(parameters)}\n \
                Indicadores: {len(calculated_indicators)}\n")
