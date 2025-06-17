import requests
import datetime
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
from economic_calendar import file
url = "https://es.investing.com/economic-calendar/Service/getCalendarFilteredData"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',  # usá el tuyo completo
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://es.investing.com/economic-calendar/",
    "Origin": "https://es.investing.com",
    # agregá las cookies si es necesario
}
# Obtener la fecha actual en formato yyyy-mm-dd
#current_date = datetime.date.today().strftime("%Y-%m-%d")
#print(current_date)
payload = {
    "country": [95, 17, 86, 52, 29, 25, 54, 114, 145, 47, 34, 8, 174, 163, 32, 70, 6, 27, 37, 107, 122, 11, 78, 15, 113, 24, 121, 59, 143, 90, 112, 26, 5, 89, 72, 45, 71, 22, 74, 51, 21, 39, 93, 14, 48, 66, 33, 106, 232, 23, 10, 119, 35, 92, 102, 57, 204, 94, 97, 68, 96, 103, 42, 111, 109, 105, 188, 7, 139, 247, 82, 172, 20, 60, 43, 87, 44, 193, 148, 125, 53, 38, 170, 4, 55, 80, 100, 56, 238, 36, 162, 110, 9, 12, 41, 46, 85, 202, 63, 61, 123, 180, 168, 138, 178, 84, 75],  # Copiá todos los IDs de país
    "importance": [1],
    "timeZone": "58",
    "timeFilter": "timeRemain",
    "currentTab": "today",
    "submitFilters": "1",
    "limit_from": "0",
}

response = requests.post(url, headers=headers, data=payload)
print(response)