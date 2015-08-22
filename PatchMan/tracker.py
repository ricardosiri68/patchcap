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
    FramesToLost = 45
    MaxFramesLosted = 300
    FramesInHypo = 3
    
    def __init__(self, tracker):
        self.bloblist = {}
        self.ts = 0
        self.lastb = 0
        self.age = 0
        self.tracker = tracker
        self.kalman = cv2.KalmanFilter(2, 1, 0)
        self.setup_kalman() 
        self.lost = -1
        states = ['hypothesis', 'entering', 'normal', 'leaving', 'lost', 'deleted']
        Machine.__init__(self, states=states, initial='hypothesis')
        r = lambda: random.randint(0,255)
        self.color = (r(),r(),r())
        # self.add_transition('enter','entering', 'normal')
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
            return

        prediction = self.kalman.predict()
        measurement = self.kalman.measurementNoiseCov * np.random.randn(1, 1)
        # generate measurement
        measurement = np.dot(self.kalman.measurementMatrix, blob.centroid) + measurement
        measurement_angle = measurement[0, 0]
        self.kalman.correct(measurement)
        process_noise = self.kalman.processNoiseCov * np.random.randn(2, 1)
        blob.centroid  = np.dot(self.kalman.transitionMatrix, blob.centroid) + process_noise


 
        if inside:
            self.to_normal()
        else:
            if self.is_normal():
                self.to_leaving()
            else:
                self.to_entering()

    def touch(self, ts):
        self.ts = ts
        self.age = self.age + 1

        if self.ts != self.lastb:
            self.lost = self.lost + 1
        if (self.is_hypothesis() and self.lost ==  BlobTracker.FramesInHypo ):
            self.to_deleted()
            return

        if self.lost == 1:
            self.to_lost()
        if self.lost == BlobTracker.MaxFramesLosted:
            self.to_deleted()

    def __contains__(self, b):
        return b == self.bloblist[self.lastb]

    def blob(self):
        if self.ts == self.lastb:
            return self.bloblist[self.lastb]
        return None

    def setup_kalman(self):
        self.kalman.transitionMatrix = np.array([[1., 1.], [0., 1.]])
        self.kalman.measurementMatrix = 1. * np.ones((1, 2))
        self.kalman.processNoiseCov = 1e-5 * np.eye(2)
        self.kalman.measurementNoiseCov = 1e-1 * np.ones((1, 1))
        self.kalman.errorCovPost = 1. * np.ones((2, 2))
        self.kalman.statePost = 0.1 * np.random.randn(2, 1)

    def __repr__(self):
        return '<BlobTracker> id: %s. ts: %s. Blob:%s. state: %s \n'%(self.id, self.ts, self.blob(), self.state)

class Tracker(object):
    def __init__(self, bgsample):
        self.be = BlobExtractor(bgsample)
        self.tracks = []
        shape = bgsample.shape[:2]
        margin = 10
        self.roi = [margin, margin, shape[1]-2*margin, shape[0]-2*margin]

    def track(self, ts, img):
        found = False
        blobs = self.be.blobs(img, ts)

        for t in self.tracks:
            for i in xrange(len(blobs) - 1, -1, -1):
                b = blobs[i]
                if b in t:
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


    def draw(self, img):
        for t in [tr for tr in self.tracks if tr.active()]:
            b = t.blob()
            x, y, w, h = b.bbox
            cv2.rectangle(img, (x, y), (x+w,y+h), t.color, thickness=3)
            #img[0:h,0:w] = b.img


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

