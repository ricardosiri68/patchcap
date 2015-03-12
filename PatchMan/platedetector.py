from timeit import default_timer as timer
from ocr import Ocr
import logging
from log import save_image
import cv2
import numpy as np
from lib.warping import ImageBlobWarping
import imutils
import sys

logger = logging.getLogger(__name__)
from logging import FileHandler, StreamHandler
from vlogging import VisualRecord


class PlateDetector(object):
    def __init__(self, vdebug = False):
        self.vdebug = vdebug
        self.ocr = Ocr('spa', logger)
        self.image = None
        self.pre = None
        self.edged = None

    def find(self, img):
        self.image = img
        edged= self.prepare(img)
        blobs = self.findBlobs(edged)
        #logger.debug('%d candidatos', len(blobs))
        for b in blobs:
            plate = self.checkBlob(b)
            if plate:
                return plate
        return None

    def findBlobs(self, img):
        rects = []
        i, cnts, hie = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            c = c.reshape(-1, 2)
            if len(c) < 4:
                continue
            arcl = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * arcl, True)
            approx = approx.reshape(-1, 2)
            if len(approx) == 4 and cv2.contourArea(approx) > 1000 and cv2.isContourConvex(approx):
                max_cos = np.max([self.angle_cos(approx[i], approx[(i+1) % 4], approx[(i+2) % 4]) for i in xrange(4)])
                if max_cos < 0.25:
                    rect = cv2.minAreaRect(approx)
                    w, h = rect[1]
                    ratio = float(w) / h if w>h else float(h) / w
                    if 3 < ratio < 4:
                        rects.append(rect)
        return rects

    def checkBlob(self, rect):
        warp = ImageBlobWarping()
        ang = rect[2]
        w = rect[1][0]
        h = rect[1][1]
        if ang<-45:
            ang = ang + 90
            w = h
            h = rect[1][0]

        box = cv2.boxPoints(rect)
        box = np.int0(box)
        box = warp.order_points(box)
        #x,y = box[0]
        #roi = img[y:y+h, x:x+w]
        #roi = imutils.rotate(roi, ang)
        roic =warp.transform(self.edged, box)
        roi =warp.transform(self.pre, box)
        if self.vdebug:
            logger.debug(VisualRecord("roi", [roi], fmt = "jpg"))
        letters = []
        i, cnts, _ = cv2.findContours(roic, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h = roic.shape[:2][0]
        if not cnts or len(cnts) < 6:
            return None
        conts = []
        for b in cnts:
            c = b.reshape(-1,2)
            if len(b)<3:
                continue
            r = cv2.boundingRect(c)
            ratio = float(r[3]) / r[2]
            if not 1.5 <= ratio <= 2.5 or r[3] < 0.5*h:
                continue
            conts.append(c)
            letters.append(r)
        cv2.drawContours(self.image,conts,-1, (0,255,0),1)
        return self.findChars(self.prepare2(roi), letters)


    def findChars(self, img, blobs):
        i = 0
        self.ocr.reset()
        for b in sorted(blobs, key=lambda b:b[0]):
            x,y,w,h = b
            l = cv2.copyMakeBorder(
                    img[y:y+h, x:x+w],
                    5, 5, 5, 5, cv2.BORDER_CONSTANT,
                    value=255)
            if self.vdebug:
                logger.debug(VisualRecord("pate", [l], fmt = "jpg"))
            if i > 2:
                readed = self.ocr.readDigit(l)
            else:
                readed = self.ocr.readText(l)
            i += 1
        return self.ocr.text()

    def prepare(self, img, scale=True):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.pre = cv2.GaussianBlur(gray, (5, 5), 0)
        # blur = cv2.adaptiveThreshold(blur, 74, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
        self.edged = cv2.Canny(self.pre, 500, 1000, apertureSize=5)

        if self.vdebug:
            logger.debug(VisualRecord("prepare", [self.edged], fmt = "jpg"))
        return self.edged

    def prepare2(self, img, scale=True):
        ret,th = cv2.threshold(img, 87, 255, cv2.THRESH_BINARY_INV)
        if self.vdebug:
            logger.debug(VisualRecord("prepare2", [th], fmt = "jpg"))
        return th


    def angle_cos(self, p0, p1, p2):
        d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
        return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

 
if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    ch = StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    fh = FileHandler("../log/debug.html", mode = "w")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    if len(sys.argv) >= 2:
        path = sys.argv[1]
    else:
        path = '/home/hernando/proyectos/patchcap/samples/images/ehy435.jpg'

    s = timer()
    f = PlateDetector(True)
    logger.info('leyendo %s', path)
    img = cv2.imread(path)
    txt = f.find(img)
    e = timer()
    logger.debug('tiempo de exe %s', (e-s))
    print txt
    logger.debug(VisualRecord("Detected edges", [img], fmt = "jpg"))
