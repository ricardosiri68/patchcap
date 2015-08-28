import common
import cv2
import logging
import numpy as np
import random

from blobs import BlobExtractor, Blob
from common import *
from sys import argv
from transitions import Machine
from logging import FileHandler, StreamHandler
from vlogging import VisualRecord

from scipy.spatial import distance

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




class BlobTracker(Machine):
    id = 0
    MaxFramesLosted = 200
    FramesInHypo = 3

    def __init__(self, tracker):
        self.bloblist = {}
        self.ts = 0
        self.lastb = 0
        self.age = 0
        self.tracker = tracker
        self.kalman = cv2.KalmanFilter(4, 2, 0)
        self.lost = 0
        states = ['hypothesis', 'entering', 'normal', 'leaving', 'lost', 'deleted']
        Machine.__init__(self, states=states, initial='hypothesis')
        r = lambda: random.randint(0,255)
        self.color = (r(),r(),r())
        #self.add_transition('enter','entering', 'normal')
        BlobTracker.id += 1
        self.id = BlobTracker.id

    def active(self):
        return self.is_normal() or self.is_entering() or self.is_leaving()

    def add(self, blob):
        self.lost = 0
        inside = blob.inside(self.tracker.roi)
        self.lastb = blob.ts
        self.bloblist[blob.ts] = blob


        if len(self.bloblist)==1:
            self.setup_kalman(blob.centroid)
            return
        else:
            self.kalman.correct(blob.centroid)

        if inside:
            self.to_normal()
        else:
            if self.is_normal():
                self.to_leaving()
            elif not self.is_leaving():
                self.to_entering()

    def touch(self, ts):
        self.ts = ts
        self.age = self.age + 1

        if self.ts != self.lastb:
            self.lost = self.lost + 1

        if self.is_hypothesis() and self.lost ==  BlobTracker.FramesInHypo:
            self.to_deleted()
            return

        self.prediction = self.kalman.predict()

        if self.lost > 0:
            self.kalman.statePost = self.kalman.statePre
            self.kalman.errorCovPost = self.kalman.errorCovPre

            if self.lost == 1:
                self.to_lost()
            elif self.lost == BlobTracker.MaxFramesLosted:
                self.to_deleted()


    def __contains__(self, b):
        last = self.bloblist[self.lastb]
        cx = self.prediction[:2]
        return (b == last) or (distance.euclidean(b.centroid, cx)<50)

    def blob(self):
        if self.ts == self.lastb:
            return self.bloblist[self.lastb]
        return None

    def cxy(self):
        return tuple(map(int,self.prediction.reshape(1,4)[0][:2]))

    def setup_kalman(self, ini):
        self.kalman.measurementMatrix = np.array([[1,0,0,0],[0,1,0,0]],np.float32)   #H
        self.kalman.transitionMatrix = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]],np.float32)
        self.kalman.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32) * 0.005 #Q
        self.kalman.errorCovPost = np.ones((4, 4), np.float32)
        self.kalman.statePost = np.array([[ini[0][0]], [ini[1][0]], [0], [0]], np.float32)

    def __repr__(self):
        return '<BT>[%s] id: %s. %s. Pre: %s'%(self.state, self.id, self.blob(), self.cxy())

class Tracker(object):
    def __init__(self, bgsample):
        self.be = BlobExtractor(bgsample)
        self.tracks = []
        shape = bgsample.shape[:2]
        margin = 10
        self.roi = [margin, margin, shape[1]-2*margin, shape[0]-2*margin]

    def track(self, ts, img):
        blobs = self.be.blobs(img, ts)

        rels = self.match(blobs)
        t.add(b)
        del blobs[i]
        t.touch(ts)

        for b in blobs:
            t = BlobTracker(self)
            t.add(b)
            t.touch(ts)
            self.tracks.append(t)

        self.tracks[:] = [x for x in self.tracks if not x.is_deleted()]
        tt = [tr for tr in self.tracks if tr.active()]
        if len(tt):
            logger.debug(tt)

    def match(self, blobs):
        b2t = {}
        t2b = {}
        unassigneds = []
        for t in reversed(self.tracks):
            if b not in b2t:
            b2t[t] = []
            for i in xrange(len(blobs) - 1, -1, -1):
            if t not in t2b:
                t2b[b] = []
                b = blobs[i]
                if b in t:
                    b2t[t].append(b)
                    t2b[b].append(t)
                elif t.contains(b):
                    b2t[t].append(b)
                else:
                    unassigneds.append(b)

        for ub in unassigneds:
            if t.contains(




    def draw(self, img):
        for t in [tr for tr in self.tracks if tr.active()]:
            b = t.blob()
            x, y, w, h = b.bbox

            cv2.circle(img,b.cxy(),4, t.color, thickness=4, lineType=8, shift=0)
            cv2.circle(img,t.cxy(),8, t.color, thickness=2, lineType=8, shift=0)
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

