import os
import logging
import cv
from SimpleCV import Image, JpegStreamCamera, VirtualCamera
import time
import urllib2
import logging
import base64

logger = logging.getLogger(__name__)

class VirtualDevice(object):
    MAX_RETRIES = 3

    _device = None
    _frames = []
    _source_type = None
    _src = None
    _fps = 15
    _onvif = False
    _errorCount = 0

    def __init__(self,src):
    
        #TODO: from config
        self._onvif = True
        
        
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
        img = None
        
        if self._source_type == 'stream':
            img = self._device.getImage()
        
        elif self._source_type in ('h264','video'):
            frame = cv.QueryFrame(self._device)
            if frame:
                img = Image(frame, cv2image=True) 
            
        else: #image,imageset
            if len(self._frames):
                img = Image(self._frames.pop())

        if img is None and self._errorCount< VirtualDevice.MAX_RETRIES:
            time.sleep(0.5)
            self._errorCount +=1
            img = self.getImage()
        
        return img
    

    def alarm(self):
        if not self._onvif:
            return False

        username = 'root'
        password = 'root'
        #http://192.168.3.20/systemlog.cgi
        auth = base64.encodestring('%s:%s' % (username, password))[:-1]
        try:
            for i in (1,0):
                req = urllib2.Request("http://192.168.3.20/portctrl.cgi&action=update&out1=%s"%i)
                req.add_header("Authorization", "Basic %s" % auth)
                resp =urllib2.urlopen(req)
                req.add_header("Authorization", "Basic %s" % auth)
                logger.debug("se disparo alarma con codigo %s y param %s",resp.code,i)
                time.sleep(1)
            return True
        except IOError, error:
            log.error(error)
        return False
