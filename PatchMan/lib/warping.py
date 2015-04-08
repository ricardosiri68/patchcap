import sys
import logging
from os import path
import cv2
import numpy as np
import time

logger = logging.getLogger(__name__)

class ImageBlobWarping(object):

    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype = "float32")
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    def transform(self, image, pts):
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[0] - bl[0]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[0] - tl[0]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[1] - br[1]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[1] - bl[1]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype = "float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        return warped


if __name__ == "__main__":
    def points(event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print x,y
    imgpath = sys.argv[1] if len(sys.argv) >= 2 else '../../samples/images/naipe.jpg'
    img =  cv2.imread(imgpath)
    w = ImageBlobWarping()
    pts = np.array([(65, 73), (162, 33), (153, 217),(271, 147)], dtype = "float32")
    
    img = w.transform (img, pts)

    cv2.namedWindow('warp')
    cv2.imshow('warp', img)
    cv2.setMouseCallback('warp', points)
    cv2.waitKey(0)
