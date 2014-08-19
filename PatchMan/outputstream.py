import logging
from SimpleCV import JpegStreamer

logger = logging.getLogger(__name__)


class OutputStream(object):

    def __init__(self):
        self.out = JpegStreamer(hostandport="localhost:8000")

    def write(self, img, plate):
        try:
            img.save(self.out)
        except:
            logger.error("sending stream...")
