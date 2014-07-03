import os
import logging
import cv2
import cv2.cv as cv
from SimpleCV import Image  # , VirtualCamera
import time
import urllib2
import base64
from motion import Motion

logger = logging.getLogger(__name__)


class VirtualDevice(object):

    _device = None
    _frames = []
    _source_type = None
    _src = None
    _fps = 15
    _onvif = False
    _errorCount = 0
    __motion = Motion()

    MAX_RETRIES = 5

    def __init__(self, src):

        #TODO: from config
        self._onvif = True
        self._src = src
        if src.startswith('http://') or\
                src.startswith('rtsp://') or src.startswith('rtp://'):
            self._source_type = 'stream'
            self._device = cv2.VideoCapture(src)
            self._fps = self._device.get(cv.CV_CAP_PROP_FPS)
        elif os.path.isdir(src):
            self._source_type = 'imageset'
            for imgfile in os.listdir(src):
                if imgfile.endswith(".jpg"):
                    self._frames.append(os.path.join(src, imgfile))

        elif src.endswith(('.jpg', '.png')):
            self._source_type = 'image'
            self._frames.append(src)
        else:
            self._source_type = 'video'
            self._device = cv.CreateFileCapture(src)
        #else: #stream
        #    self._device = Camera(src)

    def getImage(self):
        img = None

        if self._source_type in ('stream', 'video'):
            if self._source_type == 'video':
                frame = cv.QueryFrame(self._device)
                img = Image(frame, cv2image=True)
                self.__motion.detect(img)
            else:
                f, frame = self._device.read()
                if f:
                    img = Image(frame, cv2image=True)
                    self.__motion.detect(img)
        else:  # image,imageset
            if len(self._frames):
                img = Image(self._frames.pop())

        if img is None:
            time.sleep(1)
            self._errorCount += 1
            if self._errorCount < self.MAX_RETRIES:
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
            for i in (1, 0):
                req = urllib2.Request(
                    "http://192.168.3.20/portctrl.cgi&action=update&out1=%s" %
                    i
                )
                req.add_header("Authorization", "Basic %s" % auth)
                resp = urllib2.urlopen(req)
                req.add_header("Authorization", "Basic %s" % auth)
                logger.debug(
                    "se disparo alarma con codigo %s y param %s", resp.code, i
                )
                time.sleep(1)
            return True
        except IOError, error:
            logger.error(error)
        return False
