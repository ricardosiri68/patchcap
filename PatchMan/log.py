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

    def __init__(self, root):
        self.storage = root
        if not path.isdir(self.storage):
            mkdir(self.storage)
        self.l = Lock()

    def image(self,dev_id, img, ts=None):
        self.l.acquire()

	if ts:
	    name = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
        else:
            name = str(uuid.uuid4())
	
        imgpath = path.join(storage, "%s/%s.jpg" % (dev_id, name))
        if path.isfile(imgpath):
            i = 1
            imgpath = path.join(self.storage, "%s-%s.jpg" % (name, i))
            while path.isfile(imgpath):
                i += 1
                imgpath = path.join(self.storage, "%s-%s.jpg" % (name, i))
        cv2.imwrite(imgpath,img)
        self.l.release()
