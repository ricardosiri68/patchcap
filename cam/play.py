#!/usr/bin/env python
import sys
import cv2
import cv2

uri = 0
if len(sys.argv)==2:
    uri = sys.argv[1]
c = cv2.VideoCapture(uri)


    

while(1):
    _,f = c.read()
    k = cv2.waitKey(5)
    print k
    if not _ or k>0:
        break;
    cv2.imshow('e2',f)
cv2.destroyAllWindows()


