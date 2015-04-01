from timeit import default_timer as timer
import sys
import cv2
import os
from platedetector import PlateDetector
import logging 
import time

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = timer()
    finder = PlateDetector()

    if len(sys.argv)!=2:
        uri = "videotestsrc ! capsfilter caps='video/x-raw,format=BGR' ! videoconvert ! appsink"
        p = os.path.dirname(os.path.abspath(__file__))
    else:
        uri = sys.argv[1]
        tmpdir = os.path.splitext(os.path.abspath(uri))[0]
        if not os.path.exists(tmpdir):
                print 'creando directorio '+tmpdir
                os.makedirs(tmpdir)
        else:
                print 'directorio ya existe '+tmpdir

    c = cv2.VideoCapture(uri)
    cv2.namedWindow('e2',cv2.WINDOW_NORMAL)
    paused = False
    fc = 0
    while True:
        fc = fc + 1
        _, img = c.read()
        k = cv2.waitKey(20)
        if not _ or k==27:
            break;
        if k==ord('p'):
            paused = not paused
        if paused:
            time.sleep(1)
            continue
        txt, pa = finder.find2(img)
        h, w = img.shape[:2]
        if pa is not None:
            rh, rw = pa.shape[:2]
            img[h-rh:h,w-rw:w] = pa
            cv2.imwrite('{0}{1}{2}.{3}'.format(tmpdir, '/', fc,'jpg'),pa)
        if txt:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, txt, (10,500), font, 4,(255,255,255),2,cv2.LINE_AA)
        cv2.imshow('e2',img)
    e = timer()
    logging.debug('tiempo de exe %s' % (e-s))
