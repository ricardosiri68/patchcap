import sys
import os 
import logging
import stat
import time
import urllib2
import base64
from gi.repository import Gst, GObject
import urlparse

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
        
        logger.debug('configurando in %s'%url)
       
    def on_src_pad_added(self, element, pad):
        caps = pad.get_current_caps()
        print('on_src_pad_added():', caps.to_string())
        cap = caps.get_structure(0)
        if cap.get_string('media')=='video':
            pad.link(self.dec.get_static_pad('sink'))
	

    def on_dec_src_pad_added(self, element, pad):
        caps = pad.query_caps(None).to_string()
        if caps.startswith('video/'):
            print('on_pad_added():', caps)
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

def get_element_class(klass):
    element_class = GObject.type_class_peek(klass.__gtype__)
    element_class.__class__ = Gst.ElementClass
    return element_class

get_element_class(VirtualDevice).set_metadata('longname', 'classification', 'description', 'author')


def plugin_init2(plugin):
    vdt = GObject.type_register(VirtualDevice)
    res = Gst.Element.register(plugin, 'virtualdevice', 0, vdt)
    print('Registered vd?', res)
    return True

if not Gst.Plugin.register_static(Gst.VERSION_MAJOR, Gst.VERSION_MINOR, "virtualdevice", "virtualdevice src plugin", plugin_init2, '0.02', 'LGPL', 'platefinder', 'patchcap', ''):
    print "src plugin register failed"
    sys.exit()
