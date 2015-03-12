from timeit import default_timer as timer
import sys
import cv2
import os
from platedetector import PlateDetector
import logging 

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = timer()
    finder = PlateDetector()
    p = '../samples/images/'
    files = os.listdir(p)
    count = 0
    for f in files:
        img = cv2.imread(p+f)
        txt = finder.find(img)
        orig = f[:6].upper()
        if orig == txt:
            count = count + 1
        logging.debug("%s: %s"%(f[:6].upper(),txt))
    e = timer()
    logging.debug('se encontraron %s/%s', count, len(files)) 
    logging.debug('tiempo de exe %s' % (e-s))
