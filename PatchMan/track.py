from blobs import Blob
from common import *
import cv2
import numpy as np
import random
from scipy.spatial import distance
from transitions import Machine
import copy
import logging

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
#self.add_transition('enter','entering', 'normal')
logger = logging.getLogger(__name__)

class BlobTracker(Machine):
    id = 1
    MaxFramesLosted = 100
    FramesInHypo = 3
    States = ['hypothesis', 'entering', 'normal', 'leaving', 'lost', 'deleted']

    def __init__(self, tracker, blob):
        Machine.__init__(self, states=BlobTracker.States, initial='hypothesis')
        self.bloblist = {}
        self._addblob(blob)
        self.ts = blob.ts
        self.age = 1
        self.tracker = tracker
        self.kalman = cv2.KalmanFilter(4, 2, 0)
        self.setup_kalman(blob.centroid)
        r = lambda: random.randint(0,255)
        self.color = (r(),r(),r())
        self.id = BlobTracker.id
        BlobTracker.id += 1

    def active(self):
        return self.is_normal() or self.is_entering() or self.is_leaving()

    def add(self, blob):
        if self.id == 10:
            print self.ts, blob.ts

        self._addblob(blob)
        self.kalman.correct(blob.centroid)

        inside = blob.inside(self.tracker.roi)
        if inside:
            self.to_normal()
        else:
            if self.is_normal():
                self.to_leaving()
            elif not self.is_leaving():
                self.to_entering()

    def _addblob(self, blob):
        self.lost = 0
        self.lastb = blob.ts
        self.bloblist[blob.ts] = blob


    def touch(self, ts):
        self.ts = ts
        self.age += 1

        if self.is_hypothesis() and self.age == BlobTracker.FramesInHypo:
            self.to_deleted()
            return

        if self.ts != self.lastb:
            self.to_lost()
            self.lost += 1

        self.prediction = self.kalman.predict()

        if self.is_lost():
            self.kalman.statePost = self.kalman.statePre
            self.kalman.errorCovPost = self.kalman.errorCovPre

            if self.lost == BlobTracker.MaxFramesLosted:
                self.to_deleted()


    def from_group(self, blob, frame):
        last = self.bloblist[self.lastb]
        #roi, img = last.match(blob)

        #if self.id==10:
        #    cv2.imshow('blob', blob.img)

        
        roi = list(last.bbox)
        img = last.img
        dx = self.prediction[2]
        dy = self.prediction[3]
        roi[0] += dx
        roi[1] += dy
        
        if len(img):
            b = Blob.create(blob.ts, roi, self.prediction[:2], img)
            if b:
                self.append(b, frame)
            else:
                print 'errro'


    def append(self, blob, img):
        self.ts = blob.ts
        b = self.blob()
        if not b:
            self.add(blob)
            return

        bb = list(b.bbox)
        r = blob.bbox
        if r[0]<bb[0]:
            bb[0] = r[0]
        if r[1]<bb[1]:
            bb[1] = r[1]
        if r[0]+r[2] > bb[0]+bb[2]:
            bb[2] = r[0]+r[2]-bb[0]
        if r[1]+r[3] > bb[1]+bb[3]:
            bb[3] = r[1]+bb[3]-bb[1]

        cx = bb[0] + bb[2]/2
        cy = bb[1] + bb[3]/2
        roi = img[bb[1]:bb[1]+bb[3], bb[0]:bb[0]+bb[2]]
        try:
            b = Blob.create(blob.ts, tuple(bb), (cx, cy), roi)
            if b:
                self.bloblist[self.lastb] = b
        except:
            print roi.shape

    def __contains__(self, b):
        last = self.bloblist[self.lastb]
        cx = self.prediction[:2]
        d = distance.euclidean(b.centroid, cx)
        return b == last and (d<50)

    def contains(self, b):
        last = self.blob()
        if not last:
            return False
        dx = min(last.bbox[0]+last.bbox[2], b.bbox[0]+b.bbox[2]) - max(last.bbox[0], b.bbox[0])
        dy = min(last.bbox[1]+last.bbox[3], b.bbox[1]+b.bbox[3]) - max(last.bbox[1], b.bbox[1])
        sub = b.bbox[0]>last.bbox[0] and \
                b.bbox[0]+b.bbox[2] < last.bbox[0]+last.bbox[2] and \
                (distance.euclidean(b.centroid, last.centroid)<last.bbox[3])
        return (dx>=0) and (dy>=0) or sub
        

    def __getitem__(self, key):
        return self.bloblist[key]

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
        self.prediction = self.kalman.predict()

    def __repr__(self):
        return 'T[%s]: [%s]. age:%s, lost:%s'%(self.id, self.state, self.age, self.lost)


