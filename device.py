import os
from SimpleCV import Image, JpegStreamCamera, VirtualCamera
from cv import CreateFileCapture, QueryFrame

class VirtualDevice(object):
        
    _device = None
    _frames = []
    _source_type = None
    _src = None

    def __init__(self,src):
    
        self._src = src

        if src.startswith('http://') or src.startswith('rstp://') or src.startswith('rtp://'):
            self._source_type = 'stream'
            self._device = JpegStreamCamera(src)
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
            self._device = CreateFileCapture(src)
        #else: #stream
        #    self._device = Camera(src)

    def getImage(self):
        if self._source_type in ('video', 'stream'):
            img = QueryFrame(self._device)
            if img:
                if not(img.width < img.height):
                    return Image(img)

        else:
            if self._frames:
                return Image(self._frames.pop())
            else:
                return False
