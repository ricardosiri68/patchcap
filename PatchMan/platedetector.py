from timeit import default_timer as timer
from ocr import Ocr
import logging
import cv2
import numpy as np
from lib.warping import ImageBlobWarping
import sys
from multiprocessing import Pool

logger = logging.getLogger(__name__)
from logging import FileHandler, StreamHandler
from vlogging import VisualRecord


ocr = Ocr('spa', logger)

def get_start(args):
    (img, b, i) = args
    x,y,w,h = b
    l = cv2.copyMakeBorder(
            img[y:y+h, x:x+w],
            5, 5, 5, 5, cv2.BORDER_CONSTANT,
            value=255)
    if i > 2:
        return ocr.read_digit(l)
    return ocr.read_text(l)


class PlateDetector(object):
    def __init__(self, vlogger = None):
        self.vlogger = vlogger
        self.pre = None
        self.edged = None
        self.warp = ImageBlobWarping()
        self.p  = Pool(processes = 6)


    def find(self, img):
        blobs = self.findBlobs(img)
        for b in blobs:
            plate = self.checkBlob(b)
            if plate:
                return plate
        return None

    def find2(self, img):
        lastp = None
        blobs = self.findBlobs(img)
        for b in blobs:
            bb=np.int0(cv2.boxPoints(b))
            lastp = cv2.boundingRect(bb)
            plate = self.checkBlob(b)
            if plate:
                return plate, lastp
        return None, lastp

    def findContours2(self, img):
        height = img.shape[0]
        width = img.shape[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3)) # matrix of ones
        cnts = []
        for gray in cv2.split(img):# [cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)]:#
            dilated = cv2.dilate(src = gray, kernel = kernel, anchor = (-1,-1))
            blured = cv2.medianBlur(dilated, 7)
            small = cv2.pyrDown(blured, dstsize = (width / 2, height / 2))
            oversized = cv2.pyrUp(small, dstsize = (width, height)) 
            for thrs in xrange(0, 255, 26):
                if thrs == 0:
                    edges = cv2.Canny(oversized, threshold1 = 0, threshold2 = 50, apertureSize = 3)
                    next = cv2.dilate(src = edges, kernel = kernel, anchor = (-1,-1))
                else:
                    retval, next = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)

                _, contours, hierarchy = cv2.findContours(next, mode = cv2.RETR_LIST, method = cv2.CHAIN_APPROX_SIMPLE)
                cnts.extend(contours)
            self.prepare(img)
            return cnts

    def findContours(self, img):
        i = self.prepare(img)
        _, cnts, hie = cv2.findContours(i, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        return cnts

    def findBlobs(self, img):

        rects = []
        cnts = self.findContours(img)
        for c in cnts:
            c = c.reshape(-1, 2)
            if len(c) < 4:
                continue

            arcl = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * arcl, True)
            approx = approx.reshape(-1, 2)
            if len(approx) == 4 and cv2.contourArea(approx) > 3410:
                max_cos = np.max([self.angle_cos(approx[i], approx[(i+1) % 4], approx[(i+2) % 4]) for i in xrange(4)])
                if max_cos < 0.25:
                    rect = cv2.minAreaRect(approx)
                    w, h = rect[1]
                    ratio = float(w) / h if w>h else float(h) / w
                    if 2.4 < ratio < 4.2:
                        rects.append(rect)
        return rects

    def checkBlob(self, rect):
        ang = rect[2]
        w = rect[1][0]
        h = rect[1][1]
        if ang<-45:
            ang = ang + 90
            w = h
            h = rect[1][0]

        box = cv2.boxPoints(rect)
        box = np.int0(box)
        box = self.warp.order_points(box)
        roic = self.warp.transform(self.edged, box)
        roi =self.warp.transform(self.pre, box)
        
        (roich,roicw) = roic.shape[:2]
        nh = 143
        if roich>200:
            nw =  (roicw * nh)/roich
            roi =  cv2.resize(roi,(nw, nh), interpolation = cv2.INTER_LINEAR)
            roic =  cv2.resize(roic,(nw, nh), interpolation = cv2.INTER_LINEAR)


        letters = []
        i, cnts, _ = cv2.findContours(roic, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h = roic.shape[0]
        if not cnts or len(cnts) < 5:
            return None

        for b in cnts:
            c = b.reshape(-1,2)
            if len(b)<3:
                continue
            r = cv2.boundingRect(c)
            ratio = float(r[3]) / r[2]
            if not 1.5 <= ratio <= 2.5 or r[3] < 0.5*h or r[0]==1:
                continue
            letters.append(r)
        return self.findChars(self.prepare2(roi), letters)


    def findChars(self, img, blobs):
        i = 0
        letters = [(img,p[1], p[0]) for p in enumerate(sorted(blobs, key=lambda b:b[0]))]
        plate = self.p.map(get_start, letters)
        return ''.join(filter(None,plate))

    def prepare(self, img, scale=True):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.pre = cv2.GaussianBlur(gray, (5, 5), 0)
        self.edged = cv2.Canny(self.pre, 500, 1605,  apertureSize=5)

        if self.vlogger:
            self.vlogger.debug(VisualRecord("prepare", [self.pre, self.edged], fmt = "jpg"))
        return self.edged

    def prepare2(self, img, scale=True):
        kern = np.ones((3,5),np.uint8)
        th1 =  cv2.erode(img, kern, iterations = 1)
        ret,th = cv2.threshold(th1, 77, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        if self.vlogger:
            self.vlogger.debug(VisualRecord("prepare2", [img,  th1, th], fmt = "jpg"))
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
    f = PlateDetector(logger)
    img = cv2.imread(path)
    logger.debug(VisualRecord("letters", [img], fmt = "jpg"))
    txt = f.find(img)
    e = timer()
    logger.debug('tiempo de exe %s', (e-s))
    print txt
