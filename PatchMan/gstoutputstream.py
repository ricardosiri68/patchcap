import os
import logging

from gi.repository import GObject, Gst

logger = logging.getLogger(__name__)

class GstOutputStream(Gst.Bin):
    __gstdetails__ = (
        	'Create Sink device based on halcon configuration',
        	'Video Sink',
        	'w',
        	'Hernando Rojas <hrojas@lacuatro.com.ar>',
    )


    def __init__(self, src):
        super( GstOutputStream, self).__init__()
	logger.debug('configurando out %s'%src)
    	self.sink =  Gst.ElementFactory.make('autovideosink', None)
        self.add(self.sink)
	self.add_pad(
            Gst.GhostPad.new('sink', self.sink.get_static_pad('sink'))
        )

    def write(self, img, plate):
        try:
		if plate:
			img.drawText(plate)
        	img.save(self.out)
        except:
        	logger.error("sending stream...", exc_info=True)
