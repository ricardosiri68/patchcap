import os
import logging
from gi.repository import Gst

logger = logging.getLogger(__name__)


class OutputStream(Gst.Bin):
    def __init__(self):
        super().__init__()

        # Create elements
        q1 = Gst.ElementFactory.make('queue', None)
        convert = Gst.ElementFactory.make('videoconvert', None)
        scale = Gst.ElementFactory.make('videoscale', None)
        enc = Gst.ElementFactory.make('theoraenc', None)
        q2 = Gst.ElementFactory.make('queue', None)
	out = Gst.ElementFactory.make('udpsink', 'rtpsink')

	
        # Add elements to Bin
        self.add(q1)
        self.add(convert)
        self.add(scale)
        self.add(enc)
        self.add(q2)

        # Set properties
        scale.set_property('method', 3)  # lanczos, highest quality scaling

        # Link elements
        q1.link(convert)
        convert.link(scale)
        scale.link_filtered(enc,
            # Scale to 960x540, and for fun use 4:4:4 color
            Gst.caps_from_string('video/x-raw, width=960, height=540, format=Y444')
        )
        enc.link(q2)

        # Add Ghost Pads
        self.add_pad(
            Gst.GhostPad.new('sink', q1.get_static_pad('sink'))
        )
        self.add_pad(
            Gst.GhostPad.new('src', q2.get_static_pad('src'))
        )

       self.encoder2 = gst.element_factory_make("x264enc")
       self.rtp_payload2 = gst.element_factory_make("rtph264pay")
       self.rtpbin2 = gst.element_factory_make("gstrtpbin")
       self.udpsink21 = gst.element_factory_make("udpsink")
       self.udpsink21.set_property("host", "192.168.1.104")
       self.udpsink21.set_property("port", 5021)
       self.udpsink22 = gst.element_factory_make("udpsink")
       self.udpsink22.set_property("host", "192.168.1.104")
       self.udpsink22.set_property("port", 5022)
       self.udpsrc2 = gst.element_factory_make("udpsrc")
       self.udpsrc2.set_property("port", 5023)
       self.pipeline.add_many(self.src2, self.decodebin2, self.encoder2, \
                             self.rtp_payload2, self.rtpbin2, self.udpsink21, self.udpsink22, self.udpsrc2)
      
       # video 2 linking
       self.src2.link(self.decodebin2)
       self.decodebin2.connect("pad-added", onPad, self.encoder2)
       self.encoder2.link(self.rtp_payload2)
       self.rtp_payload2.link_pads('src', self.rtpbin2, 'send_rtp_sink_0')
       self.rtpbin2.link_pads('send_rtp_src_0', self.udpsink21, 'sink')
       self.rtpbin2.link_pads('send_rtcp_src_0', self.udpsink22, 'sink')
       self.udpsrc2.link_pads('src', self.rtpbin2, 'recv_rtcp_sink_0')
       
