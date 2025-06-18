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
def binance():
        logging.info("Obteniendo datos de Binance")  # Imprime mensaje indicando que se están obteniendo datos
        exchange = ccxt.binance()  # Crea una instancia del exchange Binance
        return exchange
def ohlcv(exchange,timeframe, candle_limit=None):  # Función para cargar datos y generar el gráfico de trading
    
    try:  # Inicia bloque try para capturar errores
            # Define el número de velas a obtener
        ohlcv_data = exchange.fetch_ohlcv('BTC/USDT', timeframe, limit=candle_limit,params = {"paginate": True, "paginationDirection":"backward"})  # Obtiene datos OHLCV para BTC/USDT
        if ohlcv_data == None or len(ohlcv_data) == 0:  # Verifica si se obtuvieron datos
            logging.info("Error: No se obtuvieron datos de Binance.")  # Imprime error si no hay datos
            return  # Termina la función si no hay datos
        logging.info(f"Datos obtenidos: {len(ohlcv_data)} velas")  # Imprime el número de velas obtenidas
        ohlcv_df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])  # Convierte los datos a un DataFrame
        ohlcv_df['timestamp'] = pd.to_datetime(ohlcv_df['timestamp'], unit='ms')  # Convierte la columna timestamp a formato datetime
        ohlcv_df.to_csv("data_bases/ohlcv_data.csv")
        return ohlcv_df
    except Exception as e:
        logging.info(f"Error al obtener datos de Binance: \n {e}")  # Imprime mensaje de error si falla la obtención de datos


def order_book(exchange):
    try:
        order_book = exchange.fetch_order_book('BTC/USDT',params = {"paginate": True, "paginationDirection":"backward"}) # fetchOrderBook (symbol, limit = undefined, params = {})
        logging.info(f"Order book: {order_book}")
        order_book_df = pd.DataFrame(order_book, columns=['bids', 'asks','symbol','timestamp','datetime','nonce']) 
        order_book_df.to_csv("data_bases/order_book.csv")
    except Exception as e:
        logging.info(f"Error al obtener el order book: {e}")

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
def news(topics=["blokchain","technology","economy_macro"]):
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
def feelings(url="https://api.alternative.me/fng/?limit=0"): # Todavia no funciona
    r = requests.get(url)
    r = r.json()["data"]
    rows = []
    for row in r:
        ts = int(row["timestamp"])

        if (row["value_classification"] == "Extreme Fear"):
            row["value_classification"] = -2
        elif (row["value_classification"] == "Fear"):
            row["value_classification"] = -1
        elif (row["value_classification"] == "Neutral"):
            row["value_classification"] = 0
        elif (row["value_classification"] == "Greed"):
            row["value_classification"] = 1
        elif (row["value_classification"] == "Extreme Greed"):
            row["value_classification"] = 2

        rows.append({
            "Fecha": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d"),
            "Valor": int(row["value"]),
            "Clasificación": int(row["value_classification"])
        })
    data = pd.DataFrame(rows)
    data.to_csv("data_bases/feelings.csv")
    logging.info(f"Se han guardado los datos en el archivo feelings.csv, correctamente")
    return data