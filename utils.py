import logging
import colorlog
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

