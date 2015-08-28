import cv2
import numpy as np
import logging 
logger = logging.getLogger(__name__)

class Blob(object):
    id = 0
    def __init__(self, ts, bbox, cxy, img, kp, desc):
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, True)
        self.img = img
        self.ts = ts
        self.kp = kp
        self.centroid = np.asarray(cxy, np.float32).reshape(2,1)
        self.desc = desc
        self.bbox  = bbox
        Blob.id += 1
        self.id = Blob.id

    def __eq__(self, o):
        min_matches = 25
        matches = self.matcher.match(o.desc, self.desc)
        count = len(matches)
        if count < min_matches:
            return False
        good_matches = [match for match in matches if match.distance <= 52]
        if len(good_matches) < min_matches:
            return False
       
        '''
        distances = [match.distance for match in matches]
        print min(distances)
        print max(distances)
        print 'good matches'
        print len(good_matches)
        good_distances = [match.distance for match in good_matches]
        print min(good_distances)
        print max(good_distances)

        i2 = cv2.resize(self.img, (o.img.shape[1], o.img.shape[0]))
        print i2.shape
        cv2.imshow('matches', np.hstack([o.img,i2 ]))
        '''
        return True

    '''
    return true  if blob is fully contained inside roi
    '''
    def inside(self, roi):
        return self.bbox[0] >= roi[0] and self.bbox[1] >= roi[1] and \
                self.bbox[0]+self.bbox[2] < roi[0]+roi[2] and \
                self.bbox[1]+self.bbox[3] < roi[1]+roi[3]

    def cxy(self):
        return tuple(map(int,self.centroid.reshape(1,2)[0]))

    def width(self):
        return self.bbox[2]

    def __hash__(self):
        return (self.id).__hash__()

    def __repr__(self):
        return '<Blob> id:%s %s.%s'%(self.id, self.bbox, self.cxy())


class BlobExtractor(object):

    def __init__(self, bgsample,  min_area = 2000, min_width = None, min_height = None):
        self.bgs = cv2.createBackgroundSubtractorMOG2(250, 12, False)
        self.bgs.apply(bgsample)
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        self.min_area = min_area
        self.min_width = min_width
        self.min_height = min_height
        self.detector = cv2.ORB_create()

    def blobs(self, img, ts):
        f = .25
        # frame = cv2.resize(img, (0,0),  fx=f, fy=f)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        fgmask = self.bgs.apply(img)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)
        _, cnts, hie = cv2.findContours(fgmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        blbs = []

        for c in cnts:
            c = c.reshape(-1, 2)
            if len(c) < 4 or cv2.contourArea(c)< self.min_area:
                continue
            M = cv2.moments(c)
            x, y, w, h = cv2.boundingRect(c)
            if (self.min_width and  w < self.min_width ) or \
                (self.min_height and h < self.min_height):
                continue
            roi = img[y:y+h, x:x+w]
            kp, desc = self.detector.detectAndCompute(roi, None)
            if desc is None:
                continue
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            blob = Blob(ts, (x,y,w,h),(cx, cy), roi, kp, desc)
            blbs.append(blob)
            cv2.rectangle(fgmask, (x,y), (x+w,y+h), (255,0,0), thickness=2)
        return blbs


