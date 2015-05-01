from device import VirtualDevice
from timeit import default_timer as timer
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


    def __init__(self, src, split = False):
        super( GstOutputStream, self).__init__()
        self.vsink = Gst.ElementFactory.make('intervideosink',None)
        self.add(self.vsink)
        if split:
            sink = self.add_tee()
        else:
            sink = self.vsink
        self.add_pad(Gst.GhostPad.new('sink',sink.get_static_pad('sink')))
        #vsink.get_static_pad('sink').add_probe(Gst.PadProbeType.BUFFER, self.rec_buff, 0)

    #def rec_buff(self, pad, info, data):
    #    t = timer()
    #    k = info.get_buffer().pts
    #    return Gst.PadProbeReturn.OK

    def add_tee(self):
        tee = Gst.ElementFactory.make('tee', "tee")
        q1 = Gst.ElementFactory.make('queue', None)
        xsink =  Gst.ElementFactory.make('autovideosink', None)
        q2 = Gst.ElementFactory.make('queue', None)
        self.add(tee)
        self.add(q1)
        self.add(xsink)
        self.add(q2)
      
        tee.link(q1)
        q1.link(xsink)
        
        tee.link(q2)
        q2.link(self.vsink)  
        return tee

    '''
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
    '''


