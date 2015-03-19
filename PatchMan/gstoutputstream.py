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

    def start_recording(self):
        if (self.get_setting("record-events")
            and self.get_has_valid_event_path()):
            destination = self._main_pipeline.get_by_name("destination")
            if destination:
                fn = "%s/%s_%s.ogv"%(
                    self.get_complete_event_path(),
                    datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
                    self.get_name())
                if self._recording_pipeline:
                    self._recording_pipeline.set_state(gst.STATE_NULL)
                self._recording_pipeline = gst.parse_launch("appsrc name=source ! ffmpegcolorspace ! ffenc_mpeg4 ! avimux ! filesink name=filesink location=%s"%fn)
                self._recording_pipeline.set_state(gst.STATE_PLAYING)
                logging.debug("monitor '%s' started recording '%s'"
                              %(self.get_name(), fn))
            else:
                logging.warning("monitor '%s' is missing element destination")

    def stop_recording(self):
        if self._recording_pipeline:
            source = self._recording_pipeline.get_by_name("source")
            source.emit("end-of-stream")
            fn = None
            if source:
                filesink = self._recording_pipeline.get_by_name("filesink")
                if filesink:
                    fn = filesink.get_property("location")
                    logging.debug("monitor '%s' stopped recording '%s'"
                                  %(self.get_name(), fn))
                    if self._alarm_count <= 0:
                        os.remove(fn)
                        logging.debug("removed '%s', no alarm"%fn)
                    else:
                        if self.get_setting("log-events"):
                            self.add_event_log(self.EVENT_VIDEO_RECORDED,
                                               fn)
            else:
                logging.warning("monitor '%s' recording pipeline is missing element source")
            self._recording_pipeline = None


