import common
import cv2
import logging
import numpy as np

from blobs import BlobExtractor
from track import BlobTracker
from common import *
from sys import argv
from logging import FileHandler, StreamHandler
from vlogging import VisualRecord


logger = logging.getLogger(__name__)
cap = cv2.VideoCapture(argv[1])

lat = StatValue()
cv2.namedWindow('frame')
ret, frame = cap.read()

class Tracker(object):
    def __init__(self, bgsample):
        self.be = BlobExtractor(bgsample)
        self.tracks = []
        shape = bgsample.shape[:2]
        margin = 10
        self.roi = [margin, margin, shape[1]-(2*margin), shape[0]-(2*margin)]

    def track(self, ts, img):
        blobs = self.be.blobs(img, ts)
        t2b = {}
        untracked = []

        for b in blobs:
            t2b[b] = []
            for t in reversed(self.tracks):
                if b in t:
                    t2b[b].append(t)


            tts = t2b[b]
            if len(tts)==0:
                untracked.append(b)
            elif len(tts)==1:
                tts[0].append(b, img)
            else:
                for t in tts:
                    t.from_group(b, img)

        for b in untracked:
            assigned = False
            for t in reversed(self.tracks):
                if t.contains(b):
                    t.append(b, img)
                    assigned = True
                    break
            if not assigned:
                t = BlobTracker(self, b)
                self.tracks.append(t)

        for t in self.tracks:
            t.touch(ts)

        self.tracks[:] = [x for x in self.tracks if not x.is_deleted()]
        for tt in self.tracks:
            if tt.active() or tt.id==8:
                logger.debug(tt)
        logger.debug("-----------------------------")

    def draw(self, i):
        img = i.copy()
        for t in [tr for tr in self.tracks if tr.active()]:
            b = t.blob()
            x, y, w, h = b.bbox
            if t.id==15 or t.id==16:
                cv2.imwrite(str(t.id)+'-'+str(b.id)+'.png', b.img)
            cv2.circle(img, b.cxy(),4, t.color, thickness=4, lineType=8, shift=0)
            cv2.circle(img, t.cxy(),8, t.color, thickness=2, lineType=8, shift=0)
            cv2.rectangle(img, (self.roi[0], self.roi[1]), (self.roi[0]+self.roi[2],self.roi[1]+self.roi[3]), (255,255,255), thickness=6)
            cv2.rectangle(img, (x, y), (x+w,y+h), t.color, thickness=3)
            draw_str(img,
                     (x, y+40),
                     "%s  vel %.1f %.1f %.1f " % (
                         t.id,
                         t.prediction[2][0],
                         t.prediction[3][0],
                         np.linalg.norm(t.prediction[2:])))
        return img

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    ch = StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    fh = FileHandler("../log/debug.html", mode = "w")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    ret, img = cap.read()
    img = cv2.resize(img, (940,560))
    tr = Tracker(img)

    paused = False
    step = False

    while True:
        k = cv2.waitKey(3) & 0xff
        if k == 27:
            break
        step = k == ord('s')
        if not step and k!=255:
            paused = (k == ord('p')) and not paused
        if not step and paused:
            continue

        ret, img = cap.read()
        img = cv2.resize(img, (940,560))
        ts = cv2.getTickCount()
        t = clock()
        tr.track(t, img)
        i = tr.draw(img)
        lat.update(clock()-t)
        draw_str(i, (20, 40), "latency        :  %.1f ms" % (lat.value*1000))
        cv2.imshow('frame', i)
        if step:
            paused = True
            step = False
    cap.release()
    cv2.destroyAllWindows()

