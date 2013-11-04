#!/usr/bin/env python
import cv

from  SimpleCV import Display, Image
import sys

if len(sys.argv)!=2:
    uri = "rtsp://root:root@192.168.3.20:554/cam1/onvif-h264"
else:
    uri = sys.argv[1]

video = cv.CaptureFromFile(uri)
fps = cv.GetCaptureProperty(video, cv.CV_CAP_PROP_FPS )
print fps
waitm = int( 1000/fps )
print waitm
d=Display()
while True:
    #    cv.GrabFrame(video)
    #frame = cv.RetrieveFrame(video)
    frame = cv.QueryFrame(video)
#    cv.ShowImage("IP Camera", frame)
    if not frame: continue
    i = Image(frame)
    i.save(d)
    ch = 0xFF & cv.WaitKey(1)
    if ch == 27:
        break
