import ccxt
import logging
import pandas as pd
from utils import logg_format
import requests
import pandas as pd
from bs4 import BeautifulSoup
#import coinmarketcap as cmc
import wbdata
from datetime import datetime,timezone

alphavantage_api = "VXX7JZAQDBD4GG0N"
logg_format()
def binance(apikey="zYDWPJzOj0jVT2a1OQdRlxSc6Y8Z60vbpw9lmz1tpU32U5wGnNXCtdHrkxV9gLIw",secret="asJ0B0hqMdI9JEdXqBmz804lN40KNx8dLBcueiKoFos25IBSeQvm3o4i4tLDvbDO"):
        logging.info("Obteniendo datos de Binance")  # Imprime mensaje indicando que se están obteniendo datos
        exchange = ccxt.binance({
                                "apiKey": f"{apikey}",
                                "secret": f"{secret}",
                                'enableRateLimit': True,
                                'options': {'defaultType': 'spot'}
        })  # Crea una instancia del exchange Binance
        exchange.set_sandbox_mode(True)
        return exchange
def ohlcv(exchange:ccxt.binance,timeframe:str, candle_limit:int=None):  # Función para cargar datos y generar el gráfico de trading
    try:  
        ohlcv_data = exchange.fetch_ohlcv('BTC/USDT', timeframe, limit=candle_limit)  # Obtiene datos OHLCV para BTC/USDT
        if ohlcv_data == None or len(ohlcv_data) == 0:  # Verifica si se obtuvieron datos
            logging.info("Error: No se obtuvieron datos de Binance.")  # Imprime error si no hay datos
            return None
        logging.info(f"Datos obtenidos: {len(ohlcv_data)} velas")  # Imprime el número de velas obtenidas
        ohlcv_df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])  # Convierte los datos a un DataFrame
        ohlcv_df['timestamp'] = pd.to_datetime(ohlcv_df['timestamp'], unit='ms')  # Convierte la columna timestamp a formato datetime
        ohlcv_df.to_csv("data_bases/ohlcv_data.csv")
        return ohlcv_df
    except Exception as e:
        logging.info(f"Error al obtener datos de Binance: \n {e}")  # Imprime mensaje de error si falla la obtención de datos
        return None
def OrderBook(exchange:ccxt.binance, symbol="BTCUSDT",limit:int=None):
    try:
            order_book = exchange.publicGetDepth({'symbol': f"{symbol}",'limit': limit})
            logging.info(f"Order book: \n {order_book} \n\n")
            bids = order_book.get("bids", [])
            asks = order_book.get("asks", [])
            bids = pd.DataFrame(bids, columns=["price", "quantity"])
            asks = pd.DataFrame(asks, columns=["price", "quantity"])
            logging.info(f"Bids: \n{bids} \nAsks: \n{asks} \n")
            bids.to_csv("data_bases/bids.csv", index=False)
            asks.to_csv("data_bases/asks.csv", index=False)
            return bids,asks
    except Exception as e:
        logging.info(f"Error al obtener el order book: {e}")
        return None,None


class EconomicCalendar:
    def fecha_actual():
        return pd.Timestamp.now().strftime('%Y-%m-%d')
    def extraer_eventos_con_8_columnas(html_fragment):
        soup = BeautifulSoup(f"<table>{html_fragment}</table>", "html.parser")
        rows = soup.find_all("tr")

        eventos_validos = []

        for row in rows:
            columnas = row.find_all("td")

            # Solo rows con exactamente 8 columnas
            if len(columnas) != 8:
                continue

            try:
                pais_span = columnas[1].find("span")
                pais = pais_span["title"] if pais_span else "Desconocido"
                moneda = columnas[1].get_text(strip=True).replace(pais, "").strip()
                impacto = columnas[2].get("title", "").strip()

                eventos_validos.append({
                    "Hora":      columnas[0].get_text(strip=True),
                    "País":      pais,
                    "Moneda":    moneda,
                    "Impacto":   impacto,
                    "Evento":    columnas[3].get_text(strip=True),
                    "Actual":    columnas[4].get_text(strip=True),
                    "Previsión": columnas[5].get_text(strip=True),
                    "Anterior":  columnas[6].get_text(strip=True)
                })

            except Exception as e:
                logging.info(f"Error al procesar la row: {e}")
                continue
        logging.info("Se han obtenido los eventos con 8 columnas")
        return pd.DataFrame(eventos_validos)
    def scrap():
        # URL de la API interna
        url = "https://es.investing.com/economic-calendar/Service/getCalendarFilteredData"

        # Headers (copiados del archivo que me pasaste)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://es.investing.com/economic-calendar/"
        }
        fecha = EconomicCalendar.fecha_actual()
        # Payload con todos los países, categorías e importancia alta (3 toros)
        payload = {
            "country[]": ["95","17","86","52","29","25","54","114","145","47","34","8","174","163","32","70","6","27","37","107",
                        "122","11","78","15","113","24","121","59","143","90","112","26","5","89","72","45","71","22","74","51",
                        "21","39","93","14","48","66","33","106","232","23","10","119","35","92","102","57","204","94","97","68",
                        "96","103","42","111","109","105","188","7","139","247","82","172","20","60","43","87","44","193","148",
                        "125","53","38","170","4","55","80","100","56","238","36","162","110","9","12","41","46","85","202","63",
                        "61","123","180","168","138","178","84","75"],
            "category[]": ["_employment","_economicActivity","_inflation","_credit","_centralBanks","_confidenceIndex"],
            "importance[]": ["1","2","3"],
            "dateFrom": f"{fecha}",
            "dateTo": f"{fecha}",
            "timeZone": "58",
            "timeFilter": "timeRemain",
            "limit": "0,200",
            "timeframe": "today",
            "timezoneId": "58",
            "offsetSec": "7200",
            "isFiltered": "true",
            "filterButtonState": "On"
        }

        # Convertir el payload a x-www-form-urlencoded
        data = requests.models.RequestEncodingMixin._encode_params(payload)

        # Hacer el POST
        response = requests.post(url, data=data, headers=headers)
        # Procesar el HTML que viene en el JSON
        html = response.json()['data']
        logging.info(f"HTML obtenido")
        table = EconomicCalendar.extraer_eventos_con_8_columnas(html)
        table.to_csv("data_bases/economic_calendar.csv")
        logging.info(f"Se han guardado los datos en el archivo economic_calendar.csv, correctamente")
        return table

def economic_indexs (country="USA",date=2010, indicators={"SL.EMP.TOTL.SP.ZS": "Tasa de empleo (%)","NY.GDP.MKTP.CD": "PBI total (USD)","FP.CPI.TOTL.ZG": "Inflación anual (%)","FR.INR.LEND": "Tasa de interés (%)","GC.DOD.TOTL.GD.ZS": "Deuda del gobierno (% PBI)"}):
    date = datetime.datetime(int(date), 1, 1)
    # Obtener datos
    indicators = wbdata.get_dataframe(indicators=indicators, country=country, data_date=(date, datetime.datetime.today()))
    indicators.to_csv("data_bases/economic_indexs.csv")
    logging.info(f"Se han guardado los datos en el archivo economic_indexs.csv, correctamente")
    return indicators
def marketcap():
    pass
def news(topics:list=["blokchain","technology","economy_macro"]):
    info = []
    for topic in topics:
        url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topic={topic}&sort=earliest&apikey={alphavantage_api}' 
        # Parametros opcionales: sort=EARLIEST, RELEVANCE, LATEST. tickers=IBM,MSFT. time_from & time_to = YYYYMMDDTHHMM
        r = requests.get(url)
        data = r.json() # Son diccionarios
        info.append(data)
    info = pd.DataFrame(info)
    info.to_csv("data_bases/news.csv")
    logging.info(f"Se han guardado los datos en el archivo news.csv, correctamente")
    return info
def feelings(url:str="https://api.alternative.me/fng/?limit=0"): # Todavia no funciona
    r = requests.get(url)
    r = r.json()["data"]
    rows = []
    for row in r:
        ts = int(row["timestamp"])
        emotion = row["value_classification"]
        if (emotion == "Extreme Fear"):
            emotion = -2
        elif (emotion == "Fear"):
            emotion = -1
        elif (emotion == "Neutral"):
            emotion = 0
        elif (emotion == "Greed"):
            emotion = 1
        elif (emotion == "Extreme Greed"):
            emotion = 2

        rows.append({
            "Fecha": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d"),
            "Valor": int(row["value"]),
            "Clasificación": emotion
        })
    data = pd.DataFrame(rows)
    data.to_csv("data_bases/feelings.csv")
    logging.info(f"Se han guardado los datos en el archivo feelings.csv, correctamente")
    return data
