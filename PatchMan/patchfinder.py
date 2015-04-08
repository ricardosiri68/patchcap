#!/usr/bin/env python
import log, sys
from os import path
import transaction
from daemon import Daemon
from pyramid.paster import bootstrap
from patchman.models import Plate, Device, initialize_sql
from device import VirtualDevice
from platefinder import PlateFinder
from gstoutputstream import GstOutputStream
from stats import PatchStat
from datetime import datetime
logger = log.setup()

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GstRtspServer


GObject.threads_init()
Gst.init(None)

class MyFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, pads):
        self.pads = pads
        GstRtspServer.RTSPMediaFactory.__init__(self)
        
    def do_create_pipeline(self, url):
        print 'create pipe'
        return self.pipeline
    
    def do_create_element(self, url):
        # return Gst.parse_launch("( intervideosrc ! %s ! x264enc tune=zerolatency byte-stream=true ! rtph264pay name=pay0 pt=96 )"%(self.pads))
        return Gst.parse_launch("( intervideosrc ! %s ! avenc_mpeg4 ! rtpmp4vpay name=pay0 )"%(self.pads))


class StreamServer():
    def __init__(self, pads):
        self.server = GstRtspServer.RTSPServer()
        f = MyFactory(pads)
        f.set_shared(True)
        f2 = GstRtspServer.RTSPMediaFactory()
        f2.set_launch("( intervideosrc ! %s ! x264enc bitrate=500 tune=zerolatency byte-stream=true ! rtph264pay name=pay0 pt=96 )"%(pads))
        f2.set_shared(True)
        m = self.server.get_mount_points()
        m.add_factory("/halcon", f)
        m.add_factory("/halcon2",f2)
        self.server.attach(None)


class PatchFinder(Daemon):

    def __init__(self, device_id):
        self.env = None
        super(PatchFinder, self).__init__(
            "/tmp/patchfinder.pid",
            stdin='/dev/stdin',
            stderr='/dev/stderr',
            stdout='/dev/stdout'
        )

        self.env = bootstrap(path.dirname(path.realpath(__file__))+'/development.ini')
        initialize_sql(self.env['registry'].settings)

        self.dev = Device.findBy(device_id)
        
        if not self.dev:
            logger.fatal('No existe el source %s',device_id)
            sys.exit(3)

        self.mainloop = GObject.MainLoop()
        self.pipeline = Gst.Pipeline()

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)
        self.src = VirtualDevice(self.dev.instream)
        self.src.connect('pad-added', self.on_src_pad_added)
        self.vc = Gst.ElementFactory.make("videoconvert", None)
        self.vc2 = Gst.ElementFactory.make("videoconvert", None)
        self.video = PlateFinder()

        self.sink = GstOutputStream(self.dev.outstream)

        # Add elements to pipeline
        self.pipeline.add(self.src)
        self.pipeline.add(self.vc)
        self.pipeline.add(self.video)
        self.pipeline.add(self.vc2)
        self.pipeline.add(self.sink)

        # Link elements
        self.src.link(self.vc)
        self.vc.link(self.video)
        self.video.link(self.vc2)
        self.vc2.link(self.sink)
        self.vc.link(self.sink)

        if self.dev.logging:
            logger.debug("Se escribiran los logs a la base")

    def on_src_pad_added(self, element, pad):
        print 'src pad'
        caps = pad.query_caps(None).to_string()
        print caps
        print pad.get_direction()
        if caps.startswith('video/'):
            print('on_device_src_pad_added():', caps)


    def run(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        s = StreamServer('video/x-raw, width=1920, height=1080,interlace-mode=progressive, chroma-site=mpeg2, colorimetry=bt709, framerate=25/1')
        self.mainloop.run()

    def kill(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.mainloop.quit()
        self.stop()

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.ERROR or t == Gst.MessageType.EOS:
            self.kill()
            err, debug = message.parse_error()
            error = str(err)
            if debug:
                error += " (%s)"%debug
                logger.error("monitor '%s' received error; %s"%(self.dev, error))
        elif t == Gst.MessageType.STATE_CHANGED:
            old, state, pending = message.parse_state_changed()
            if state == Gst.State.NULL:
                logger.info("monitor '%s' main pipeline is stopped"% self.dev)                
                self.kill()
            elif state == Gst.State.PLAYING:
                logger.info("monitor '%s' main pipeline is playing"% self.dev.name)                


    def log(self, img, code, stats):
        stats.detected()
        if self.dev.logging:
            logger.debug("loging capture to db")
            transaction.begin()
            plate = Plate.findBy(code)
            if plate.active:
                self.src.alarm()
            plate.log()
            transaction.commit()
        ts=datetime.now().strftime("%Y%m%d-%H%M%S")
        log.save_image(img,code+ts,'log/')
        if img.filename:
            real = path.splitext(path.basename(img.filename))[0].upper()
            output = code.upper().replace(" ","")[:6]
            if output == real[:6]:
                logger.debug("\033[92m" + output + ": OK \033[0m")
                stats.found()
            else:
                logger.debug(real[:6] + ": " + output)

    def __del__(self):
        self.kill()
        self.src = None
        if self.env:
            self.env['closer']()
            del self.env





if __name__ == "__main__": 
    daemon = PatchFinder(sys.argv[2])
    if len(sys.argv) >= 2:
        if 'start' == sys.argv[1]:
                daemon.start()
        elif 'stop' == sys.argv[1]:
                daemon.stop()
        elif 'restart' == sys.argv[1]:
                daemon.restart()
        else:
            print "comando desconocido"
	    sys.exit(2)
        sys.exit(0)
    else:
        print "uso: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
