import os
import logging
import stat 
import time
import urllib2
import base64
from motion import Motion
from gi.repository import Gst
import urlparse

logger = logging.getLogger(__name__)


class VirtualDevice(Gst.Bin):
    _device = None
    _frames = []
    _source_type = None
    _src = None
    _fps = 15
    _onvif = False
    _errorCount = 0
    __motion = Motion()

    MAX_RETRIES = 5

    __gstdetails__ = (
        	'Open device based on halcon configuration',
        	'Video Source',
        	'quesoy',
        	'Hernando Rojas <hrojas@lacuatro.com.ar>',
    )


    def __init__(self, url):
	res = urlparse.urlparse(url)
        super(VirtualDevice, self).__init__()

	#pipeline = gst.parse_launch('rtspsrc name=source latency=0 ! decodebin ! autovideosink')
	#source = pipeline.get_by_name('source')
	#source.props.location = 'rtsp://192.168.0.127/axis-media/media.amp'
	if res.scheme == "http":
        	self.src = Gst.ElementFactory.make('souphttpsrc', 'source')
            	self.src.set_property("uri", url)
    	elif res.scheme == "rtsp":
        	self.src = Gst.ElementFactory.make('rtspsrc', None)
            	self.src.set_property("location", url)
    	elif res.scheme == "file" or not res.scheme:
        	try:
            		st = os.stat(res.path)
        		if stat.S_ISCHR(st.st_mode):
            			self.src = Gst.ElementFactory.make("v4l2src", "source")
            			self.src.set_property("device", res.path)
        		else:
	    			self.src = Gst.ElementFactory.make("filesrc", "source")
            			self.src.set_property("location", res.path)
        	except IOError, e:
			self.src = Gst.ElementFactory.make("videotestsrc", "source")
            		logging.error("unable to parse URL '%s': %s"%(url, e))
	    	
	self.src.connect('pad-added', self.on_src_pad_added)
	self.dec = Gst.ElementFactory.make('decodebin', None)
	self.dec.connect('pad-added', self.on_dec_src_pad_added)
	self.add(self.src)
        self.add(self.dec)

	self.video_pad = Gst.GhostPad.new_no_target("video_pad",  Gst.PadDirection.SRC) 
	self.add_pad(self.video_pad)
	 
	logger.debug('configurando in %s'%url)
       
    def on_src_pad_added(self, element, pad):
	#string = pad.query_caps(None).to_string()
	caps = pad.get_current_caps()
        print('on_src_pad_added():', caps.to_string())
	cap = caps.get_structure(0)
        if cap.get_string('media')=='video':
            pad.link(self.dec.get_static_pad('sink'))
	

    def on_dec_src_pad_added(self, element, pad):
        string = pad.query_caps(None).to_string()
        print('on_pad_added():', string)
        if string.startswith('video/'):
		#pad.link(self.scale.get_static_pad('sink'))
		#self.scale.link(self.rate)
		#self.rate.link(self.filter)
		self.video_pad.set_target(pad)


    def alarm(self):
        if not self._onvif:
            return False

        username = 'admin'
        password = 'admin'
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

    def __repr__(self):
	    return self.__str__()

    def __str__(self):
	    return self.name + "[%s]"%self.src  
