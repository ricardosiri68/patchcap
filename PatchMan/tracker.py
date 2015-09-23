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

'''
hint for transitions:
self.is_{state}()
self.on_enter_{state}()
self.on_exit_{state}()
self.set_state('')
self.to_{state}()
transitions = [
['trigger', 'source', 'dest'],
['trigger', 'source', 'dest']
]    
'''

class Tracker(object):
    def __init__(self, bgsample):
        self.be = BlobExtractor(bgsample)
        self.tracks = []
        shape = bgsample.shape[:2]
        margin = 10
        self.roi = [margin, margin, shape[1]-2*margin, shape[0]-2*margin]

    def track(self, ts, img):
        blobs = self.be.blobs(img, ts)
        b2t = {}
        t2b = {}
        untracked = []

        for t in reversed(self.tracks):
            t.touch(ts)
            b2t[t] = []
            for b in blobs:
                t2b[b] = []
                if b in t:
                    b2t[t].append(b)
                    t2b[b].append(t)

        for t in b2t:
            bbs = b2t[t]
            if len(bbs)==0:
                continue
            if len(bbs)==1:
                t.add(bbs[0])
            else:
                t.merge(bbs, img)

        
        unassigneds = [b for b in blobs if b not in t2b or len(t2b[b])==0]
        for t in reversed(self.tracks):
            for ub in unassigneds:
                if t.contains(ub):
                    t.combine(ub, img)
                    t2b[ub].append(t)

        untracked = [b for b in blobs if b not in t2b or len(t2b[b])==0]

        for b in untracked:
            t = BlobTracker(self)
            t.add(b)
            t.touch(ts)
            self.tracks.append(t)


        self.tracks[:] = [x for x in self.tracks if not x.is_deleted()]
        for tt in self.tracks:
            logger.debug(tt)
        logger.debug("-----------------------------")

    def draw(self, img):
        for t in [tr for tr in self.tracks if tr.active()]:
            b = t.blob()
            x, y, w, h = b.bbox

            cv2.circle(img, b.cxy(),4, t.color, thickness=4, lineType=8, shift=0)
            cv2.circle(img, t.cxy(),8, t.color, thickness=2, lineType=8, shift=0)
            cv2.rectangle(img, (x, y), (x+w,y+h), t.color, thickness=3)
            draw_str(img,
                     (x, y+20),
                     "%s  vel %.1f %.1f %.1f " % (
                         t.id,
                         t.prediction[2][0],
                         t.prediction[3][0],
                         np.linalg.norm(t.prediction[2:])))

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    ch = StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    fh = FileHandler("../log/debug.html", mode = "w")
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    ret, img = cap.read()
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
        tr.draw(img)
        lat.update(clock()-t)
        draw_str(img, (20, 40), "latency        :  %.1f ms" % (lat.value*1000))
        cv2.imshow('frame', img)
        if step:
            paused = True
            step = False
    cap.release()
    cv2.destroyAllWindows()

