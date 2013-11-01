import os
from SimpleCV import Image, JpegStreamCamera, VirtualCamera


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
        elif src.endswith(('jpg','png')):
            self._source_type = 'image'
            self._frames.append(src) 
        else:
            self._source_type = 'video'
            self._device = VirtualCamera(src,"video")
        #else: #stream
        #    self._device = Camera(src)

    def getImage(self):
        if self._source_type in ('video', 'stream'):
            return self._device.getImage()
        else:
            if len(self._frames):
                return Image(self._frames.pop())
        return None
