from timeit import default_timer as timer
import base64
import logging
import os 
import stat
import sys
import time
try:
    import urllib.request as urllib2
    import urllib.parse as urlparse
except ImportError:
    import urllib2
    import urlparse

from gi.repository import Gst, GObject

logger = logging.getLogger(__name__)

GObject.threads_init()
Gst.init(None)


class VirtualDevice(Gst.Bin):

    __gstmetadata__ = (
            'Open device based on halcon configuration',
        	'Video Source',
        	'quesoy',
        	'Hernando Rojas <hrojas@lacuatro.com.ar>'
    )

    def __init__(self, url):
        res = urlparse.urlparse(url)
        super(VirtualDevice, self).__init__()

        if res.scheme == "http":
            self.src = Gst.ElementFactory.make('souphttpsrc', 'source')
            self.src.set_property("uri", url)
        elif res.scheme == "rtsp":
            self.src = Gst.ElementFactory.make('rtspsrc', None)
            self.src.set_property("location", url)
        elif res.scheme == "file" or not res.scheme:
            try:
                if os.path.isfile(res.path):
                    self.src = Gst.ElementFactory.make("filesrc", "source")
                    self.src.set_property("location", res.path)
                else:
                    st = os.stat(res.path)
                    if stat.S_ISCHR(st.st_mode):
                        self.src = Gst.ElementFactory.make("v4l2src", "source")
                        self.src.set_property("device", res.path)
            except Exception as e:
                self.src = Gst.ElementFactory.make("videotestsrc", "source")
                logging.error("unable to parse URL '%s': %s"%(url, e))

        self.dec = Gst.ElementFactory.make('decodebin', None)
        self.dec.connect('pad-added', self.on_dec_src_pad_added)
        self.add(self.src)
        self.add(self.dec)
 
        if self.src.get_static_pad('src'):
            self.src.link(self.dec)
        else:
            self.src.connect('pad-added', self.on_src_pad_added)

        self.video_pad = Gst.GhostPad.new_no_target("video_pad",  Gst.PadDirection.SRC) 
        self.add_pad(self.video_pad)
        #self.video_pad.connect('linked', self.on_deco_pad_linked)
       
    #def on_deco_pad_linked(self, pad, peer):
    #    pad.add_probe(Gst.PadProbeType.BUFFER, self.rec_buff, 0)

    # used to log buffer timestamps
    # def rec_buff(self, pad, info, data):
    #    VirtualDevice.gt[info.get_buffer().pts] = timer()
    #    return Gst.PadProbeReturn.OK

    def on_src_pad_added(self, element, pad):
        caps = pad.get_current_caps()
        cap = caps.get_structure(0)
        if cap.get_string('media')=='video':
            pad.link(self.dec.get_static_pad('sink'))

    def on_dec_src_pad_added(self, element, pad):
        caps = pad.get_current_caps()
        if caps.to_string().startswith('video/'):
            self.video_pad.set_target(pad)
            self.post_message(Gst.Message.new_application(self, caps.get_structure(0)))


    def __repr__(self):
	    return self.__str__()

    def __str__(self):
	    return self.name + "[%s]"%self.src 

GObject.type_register(VirtualDevice)
__gstelementfactory__ = ("halcondevice", Gst.Rank.NONE, VirtualDevice)



