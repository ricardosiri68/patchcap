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
    def __init__(self):
        self.ocr = Ocr('spa', logger)

    def find(self, img):
        optimg = self.prepare(img)
        # logger.debug(VisualRecord("bin", [optimg], fmt = "jpg"))
        blobs = self.findBlobs(optimg, img)
        # logger.debug('%d candidatos', len(blobs))
        for b in blobs:
            plate = self.checkBlob(optimg, b)
            if plate:
                return plate

    def findBlobs(self, img, orig):
        rects = []
        i, cnts, hie = cv2.findContours(img.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            c = c.reshape(-1,2)
            if len(c)<4: continue
            arcl = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * arcl, True)
            approx = approx.reshape(-1,2)
            if len(approx) == 4 and cv2.contourArea(approx) > 1000 and cv2.isContourConvex(approx):
                max_cos = np.max([self.angle_cos( approx[i], approx[(i+1) % 4], approx[(i+2) % 4] ) for i in xrange(4)])
                if max_cos < 0.25:
                    rect  = cv2.minAreaRect(approx)
                    cv2.drawContours(orig,[approx], -1, (0,255,0), 1)
                    w, h = rect[1]
                    ratio = float(w) / h if w>h else float(h) / w
                    if 3 < ratio < 4:
                        rects.append(rect)
        return rects

   def checkBlob(self, img, rect):
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
        roi = warp.transform(img, box)
        # logger.debug(VisualRecord("roi", [roi], fmt = "jpg"))
        letters = []
        i, cnts, _ = cv2.findContours(roi.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts or len(cnts) < 6:
            return None
        for b in cnts:
            c = b.reshape(-1,2)
            if len(b)<3:
                continue
            r = cv2.boundingRect(c)
            ratio = float(r[3]) / r[2]
            if not 1.75 <= ratio <= 3:
                continue
            letters.append(r)
        return self.findChars(roi, letters)


    def findChars(self, img, blobs):
        i = 0
        self.ocr.reset()
        for b in sorted(blobs, key=lambda b:b[0]):
            x,y,w,h = b
            l = cv2.copyMakeBorder(
                    img[y:y+h, x:x+w],
                    5, 5, 5, 5, cv2.BORDER_CONSTANT,
                    value=0)
            # logger.debug(VisualRecord("pate", [l], fmt = "jpg"))
            if i > 2:
                readed = self.ocr.readDigit(l)
            else:
                readed = self.ocr.readText(l)
            i += 1
        return self.ocr.text()

    def prepare(self, img, scale=True):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gb = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(gb, 75, 200)
        return edged

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
    f = PlateDetector()
    logger.info('leyendo %s', path)
    img = cv2.imread(path)
    txt = f.find(img)
    e = timer()
    logger.debug('tiempo de exe %s', (e-s))
    logger.debug('encontrado %s',txt)
    logger.debug(VisualRecord("Detected edges", [img], fmt = "jpg"))
