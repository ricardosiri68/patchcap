import os
import logging
import cv
from SimpleCV import Image, JpegStreamCamera, VirtualCamera
import time

logger = logging.getLogger(__name__)

class VirtualDevice(object):
        
    _device = None
    _frames = []
    _source_type = None
    _src = None
    _fps = 15

    def __init__(self,src):
    
        self._src = src

        if src.startswith('http://') :
            self._source_type = 'stream'
            self._device = JpegStreamCamera(src)
        elif src.startswith('rtsp://') or src.startswith('rtp://'):
            self._source_type = 'h264'
            self._device = cv.CaptureFromFile(src)
            self._fps = cv.GetCaptureProperty(self._device, cv.CV_CAP_PROP_FPS )
        elif os.path.isdir(src):
            self._source_type = 'imageset'
            for imgfile in os.listdir(src):
                if imgfile.endswith(".jpg"):
                    self._frames.append(os.path.join(src, imgfile))

        elif src.endswith(('.jpg','.png')):
            self._source_type = 'image'
            self._frames.append(src) 
        else:
            self._source_type = 'video'
            self._device = cv.CreateFileCapture(src)
        #else: #stream
        #    self._device = Camera(src)
            
    def getImage(self):
        if self._source_type == 'stream':
            return self._device.getImage()

        elif self._source_type in ('h264','video'):
            frame = cv.QueryFrame(self._device)
            if not frame:
                logger.warn("no se pudo leer frame")
                return None
            time.sleep(int(1/self._fps))
            return Image(frame, cv2image=True) 

        else: #image,imageset
            if len(self._frames):
                return Image(self._frames.pop())
