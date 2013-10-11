import logging, logging.handlers
import math

def setup():

    formatter = logging.Formatter(fmt='%(asctime)s - %(module)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter(fmt='%(message)s')
    console = logging.StreamHandler()
    console.setFormatter(console_formatter)
    console.setLevel(logging.DEBUG)

    rotating_file = logging.handlers.RotatingFileHandler("logs/patchcap.log", mode = 'a', maxBytes = 10*math.pow(1024,3), backupCount=45)
    rotating_file.setFormatter(formatter)
    rotating_file.setLevel(logging.WARNING)

    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    logger.addHandler(console)
    logger.addHandler(rotating_file)


    return logger
