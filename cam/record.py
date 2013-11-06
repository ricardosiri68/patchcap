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
w = (int)(cv.GetCaptureProperty(video, cv.CV_CAP_PROP_FRAME_WIDTH ))
h = (int)(cv.GetCaptureProperty(video, cv.CV_CAP_PROP_FRAME_HEIGHT ))
writer = cv.CreateVideoWriter(filename="out.avi",fourcc=cv.CV_FOURCC('F','M','P','4'),fps=fps, frame_size=(w,h),is_color=True)

print "fps: "+str(fps)
print "w: "+str(w)
print "h: "+str(h)

waitm = int( 1000/fps )
print waitm
d=Display()
while True:
    frame = cv.QueryFrame(video)
    if not frame: continue
    cv.WriteFrame(writer, frame)
    i = Image(frame)
    i.save(d)
    ch = 0xFF & cv.WaitKey(waitm)
    if ch == 27:
        break
del writer
