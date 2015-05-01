#!/usr/bin/env python
import sys
import logging
import gi
import transaction
from os import path
from datetime import datetime
from pyramid.paster import bootstrap
import patchman
from patchman.models import Plate, Device, initialize_sql

from daemon import Daemon
from device import VirtualDevice
import log
from platefinder import PlateFinder
from gstoutputstream import GstOutputStream
from stats import PatchStat

logger = log.setup()

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GstRtspServer


GObject.threads_init()
Gst.init(None)

class MyFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, fmt):
        self.fmt = fmt
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.set_shared(True)
        
    def do_create_element(self, url):
        if self.fmt == 'mp4':
            pipe = "( intervideosrc ! videoconvert ! avenc_mpeg4 ! rtpmp4vpay name=pay0 )"
        elif self.fmt =='h264':
            pipe = "( intervideosrc ! videoconvert ! vaapipostproc ! vaapiencode_h264 ! rtph264pay name=pay0 pt=96 )"
        return Gst.parse_launch(pipe)


class StreamServer():
    def __init__(self, name):
        self.server = GstRtspServer.RTSPServer()
        m = self.server.get_mount_points()
        m.add_factory("/{0}/mp4".format(name), MyFactory('mp4'))
        m.add_factory("/{0}/h264".format(name),MyFactory('h264'))
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

        self.env = bootstrap(path.dirname(path.realpath(__file__))+'/halcon.ini')
        initialize_sql(self.env['registry'].settings)
        self.caps = None
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
        self.vc1 = Gst.ElementFactory.make('videoconvert', None)
        self.video = PlateFinder(self.dev)
        self.sink = GstOutputStream(self.dev.outstream, split=False)

        self.pipeline.add(self.src)
        self.pipeline.add(self.vc1)
        self.pipeline.add(self.video)
        self.pipeline.add(self.sink)
        self.src.link(self.vc1)
        self.vc1.link(self.video)
        self.video.link(self.sink)

    def run(self):
        if logger.isEnabledFor(logging.DEBUG):
            Gst.debug_bin_to_dot_file_with_ts(self.pipeline, Gst.DebugGraphDetails.ALL, 'halcon')
        try:
            self.pipeline.set_state(Gst.State.PLAYING)
            self.mainloop.run()
        except KeyboardInterrupt:
            logger.warning("Cancelando por Ctrl-C")
            self.kill()
            raise KeyboardInterrupt

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
                logger.info("monitor '%s' main pipeline is stopped"% self.dev.name)
                self.kill()
            elif state == Gst.State.PLAYING:
                if message.src == self.pipeline:
                    logger.info("'%s' cambio de %s a %s. Pending: %s"%(self.dev.name, self.get_state(old), self.get_state(state), self.get_state(pending))) 
                    s = StreamServer(self.dev.outstream)
        elif t == Gst.MessageType.APPLICATION and message.has_name('video/x-raw'):
            s = message.get_structure()
            self.caps = s.to_string()
            if self.caps.endswith(';'):
                self.caps = self.caps[:-1]
        elif t == Gst.MessageType.INFO:
            e, d = message.parse_info()
            logger.debug("{0}: {1}", e, d)
        elif t == Gst.MessageType.WARNING:
            e, d = message.parse_warning()
            error = str(e)
            if d:
                error += " (%s)"%d
                logger.warn("monitor '%s' received warning; %s"%(self.dev, error))


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

    def get_state(self, state):
        if state == Gst.State.PLAYING:
            return "playing"
        elif state == Gst.State.READY:
            return "ready"
        elif state == Gst.State.PAUSED:
            return "paused"
        elif state == Gst.State.VOID_PENDING:
            return "pending"
        else:
            return "null"


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
            print("comando desconocido")
        sys.exit(2)
        sys.exit(0)
    else:
        print("uso: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
