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
from gi.repository import GObject, Gst


GObject.threads_init()
Gst.init(None)

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

        if self.dev.logging:
            logger.debug("Se escribiran los logs a la base")

    def run(self):
        self.pipeline.set_state(Gst.State.PLAYING)
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
