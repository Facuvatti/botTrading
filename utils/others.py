import logging
import colorlog
import inspect
import pandas as pd
import random
from utils.artificial_inteligence import aiDecides #para debug
def umbral (x, margin):
    distance = x*margin
    up = x + distance
    down = x - distance
    return up, down
def logg_format():
    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red'
    }

    formatter = colorlog.ColoredFormatter(
        "| %(filename)s | L %(lineno)d | %(log_color)s%(levelname)-8s%(reset)s: %(message)s",
        log_colors=log_colors
    )

    logger = logging.getLogger()

    # Evita agregar múltiples handlers al logger
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)  # Cambiar según necesidad

def get_variable_name(variable):
    frame = inspect.currentframe().f_back
    for name, value in frame.f_locals.items():
        if value is variable:
            return name
    return None
def read_csv_in_chunks(file_name): #Para archivos con muchisimos datos
    for i, chunk in enumerate(pd.read_csv(file_name, chunksize=1000)):
        print("chunk#{}".format(i))
        print(chunk)
def aleatory_list(size, min, max, isFloat=False): # Para debug
    return [aiDecides(min,max,isFloat) for _ in range(size)]