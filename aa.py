import requests
import pandas as pd
from bs4 import BeautifulSoup
from economic_calendar import file
from io import StringIO
# URL de la API interna
url = "https://es.investing.com/economic-calendar/Service/getCalendarFilteredData"

# Headers (copiados del archivo que me pasaste)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://es.investing.com/economic-calendar/"
}

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
    "dateFrom": "2025-06-17",
    "dateTo": "2025-06-17",
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
html_table = response.json()['data']
html_table = f"<table>{html_table}</table>"
file(html_table, "table.html")

soup = BeautifulSoup(html_table, "html.parser")
file(soup, "soup.html")
table = soup.prettify()
# Parsear con pandas (o seguir usando BeautifulSoup si preferís más control)
table = pd.read_html(StringIO(table))
print(type(table), table)

