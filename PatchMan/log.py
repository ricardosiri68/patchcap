import logging
from logging.config import fileConfig
import logging.handlers
import math
import uuid
from os import path, mkdir
import cv2
import ConfigParser
from multiprocessing import Lock

def logger(name = None):
    fileConfig(path.dirname(path.realpath(__file__))+"/condor.ini")
    return logging.getLogger(name)

class ImageLogger(object):

    def __init__(self, dev_id):
        config = ConfigParser.ConfigParser()
        config.read(path.dirname(path.realpath(__file__))+"/condor.ini")
        storage_root = config.get('condor', 'storage')
        self.storage = path.join(storage_root, str(dev_id))
        if not path.isdir(self.storage):
            mkdir(self.storage)
        self.l = Lock()

    def image(self, img, name =''):
        self.l.acquire()
        if not name:
            name = str(uuid.uuid4())
        
        imgpath = path.join(self.storage, "%s.png" % (name))
        if path.isfile(imgpath):
            i = 1
            imgpath = path.join(self.storage, "%s-%s.png" % (name, i))
            while path.isfile(imgpath):
                i += 1
                imgpath = path.join(self.storage, "%s-%s.png" % (name, i))
        cv2.imwrite(imgpath,img)
        self.l.release()
