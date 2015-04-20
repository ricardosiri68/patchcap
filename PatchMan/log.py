import logging
import logging.handlers
import math
import uuid
from os import path, mkdir
import cv2


def setup():

    format = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt=format)
    console_formatter = logging.Formatter(fmt='%(message)s')
    console = logging.StreamHandler()
    console.setFormatter(console_formatter)
    console.setLevel(logging.DEBUG)

    rotating_file = logging.handlers.RotatingFileHandler(
        path.dirname(path.dirname(path.realpath(__file__)))+"/log/patchcap.log",
        mode='a',
        maxBytes=10 * math.pow(1024, 3),
        backupCount=45
    )
    rotating_file.setFormatter(formatter)
    rotating_file.setLevel(logging.WARNING)

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)
    logger.addHandler(rotating_file)

    return logger

def log_image(img, name ='', images_path= '../log/'):
    if not path.isdir(images_path):
        mkdir(images_path)

    if not name:
        name = str(uuid.uuid4())

    imgpath = path.join(images_path, "%s.png" % (name))
    if path.isfile(imgpath):
        i = 1
        imgpath = path.join(images_path, "%s-%s.png" % (name, i))
        while path.isfile(imgpath):
            i += 1
            imgpath = path.join(images_path, "%s-%s.png" % (name, i))
    cv2.imwrite(imgpath,img)
