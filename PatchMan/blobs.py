import cv2
import numpy as np
import logging
logger = logging.getLogger(__name__)

class Blob(object):
    id = 0

    @classmethod
    def create(cls, ts, bbox, cxy, img):
        blob = cls(ts, bbox, cxy, img)
        if blob.desc is None:
            return None
        return blob

    def __init__(self, ts, bbox, cxy, img):
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, True)
        self.img = img
        self.ts = ts
        self.centroid = np.asarray(cxy, np.float32).reshape(2,1)
        self.bbox  = bbox
        Blob.id += 1
        self.id = Blob.id
        self.detector = cv2.ORB_create()
        self.kp, self.desc = self.detector.detectAndCompute(img, None)


    def match(self, blob):
        kp, desc = self.detector.detectAndCompute(blob.img, None)
        matches = self.matcher.match(desc, trainDescriptors = self.desc)
        cnt = [kp[m.queryIdx].pt for m in matches if m.distance < 16]
        if len(cnt)<5:
            logger.warn('No match')
            return [], []
        roi = list(cv2.boundingRect(np.asarray(cnt,dtype=int)))
        matched = blob.img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
        roi[0] += blob.bbox[0]
        roi[1] += blob.bbox[1]

#        outImg = blob.img
#        outImg = cv2.drawMatches(blob.img, kp, self.img, self.kp, matches[:5], outImg )
#        cv2.imshow('matches',
#                np.hstack([
#                    cv2.resize(self.img,(200,200)),
#                    cv2.resize(blob.img,(200,200)),
#                    cv2.resize(matched,(200,200))
#                ])
#            )
#        cv2.imshow('match', outImg)
#        cv2.imwrite('match-'+str(blob.id)+'.png', outImg)
        
        return roi, matched


    '''
    return true  if blob is fully contained inside roi
    '''
    def inside(self, roi):
        return self.bbox[0] >= roi[0] and self.bbox[1] >= roi[1] and \
                (self.bbox[0]+self.bbox[2]) < (roi[0]+roi[2])    and \
                self.bbox[1]+self.bbox[3] < roi[1]+roi[3]

    def cxy(self):
        return tuple(map(int,self.centroid.reshape(1,2)[0]))

    def width(self):
        return self.bbox[2]

    def __eq__(self, o):
        min_matches =  30
        try:
            matches = self.matcher.match(o.desc, trainDescriptors = self.desc)
            count = sum(1 for m in matches if m.distance < 50)
        except:
            print o.desc
            print self.desc
            count = 0
        return count >= min_matches

    def __hash__(self):
        return (self.id).__hash__()

    def __repr__(self):
        return '<Blob> id:%s %s.%s'%(self.id, self.bbox, self.cxy())


class BlobExtractor(object):

    def __init__(self, bgsample,  min_area = 2000, min_width = None, min_height = None):
        self.bgs = cv2.createBackgroundSubtractorMOG2(100, 8, False)
        self.bgmask = self.bgs.apply(bgsample)
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        self.min_area = min_area
        self.min_width = min_width
        self.min_height = min_height
        

    def blobs(self, img, ts):
        f = .25
        # frame = cv2.resize(img, (0,0),  fx=f, fy=f)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        self.fgmask = self.bgs.apply(img)
        self.fgmask = cv2.morphologyEx(self.fgmask, cv2.MORPH_OPEN, self.kernel)
        _, cnts, hie = cv2.findContours(self.fgmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        blbs = []

        for c in cnts:
            c = c.reshape(-1, 2)
            if len(c) < 4 or cv2.contourArea(c)< self.min_area:
                continue
            x, y, w, h = cv2.boundingRect(c)
            if (self.min_width and  w < self.min_width ) or \
                (self.min_height and h < self.min_height):
                continue
            roi = img[y:y+h, x:x+w]
            M = cv2.moments(c)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            blob = Blob.create(ts, (x,y,w,h),(cx, cy), roi)
            if blob:
                blbs.append(blob)

        return blbs


