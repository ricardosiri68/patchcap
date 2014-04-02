import logging
import logging.handlers
import math
import uuid
from os import path, mkdir


def setup():

    format = '%(asctime)s - %(module)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt=format)
    console_formatter = logging.Formatter(fmt='%(message)s')
    console = logging.StreamHandler()
    console.setFormatter(console_formatter)
    console.setLevel(logging.DEBUG)

    rotating_file = logging.handlers.RotatingFileHandler(
        "logs/patchcap.log",
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


def save_image(img, name=''):

    filename = None
    images_path = "blobsChars/"
    if not path.isdir(images_path):
        mkdir(images_path)

    if img.filename:
        filename = path.splitext(path.basename(img.filename))[0].upper()
        images_path += filename
        if not path.isdir(images_path):
            mkdir(images_path)

    if not name:
        if filename is None:
            filename = str(uuid.uuid4())
        name = filename

    imgpath = path.join(images_path, "%s.png" % (name))
    if path.isfile(imgpath):
        i = 1
        imgpath = path.join(images_path, "%s-%s.png" % (name, i))
        while path.isfile(imgpath):
            i += 1
            imgpath = path.join(images_path, "%s-%s.png" % (name, i))
    img.save(imgpath)
