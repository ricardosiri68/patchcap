#!/usr/bin/env python
import sys
import gi
import transaction
from os import path
from datetime import datetime
from time import sleep
from device import VirtualDevice
from log import logger
from platefinder import PlateFinder
from gstoutputstream import GstOutputStream
from stats import PatchStat
from client import Backend

log = logger()

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GstRtspServer


GObject.threads_init()
Gst.init(None)

class MyFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, fmt, name):
        self.fmt = fmt
        self.name = name
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.set_shared(True)
        self.vaapi_enabled = Gst.ElementFactory.make('vaapipostproc', None)

    def do_create_element(self, url):
        if self.fmt == 'mp4':
            pipe = "( intervideosrc channel=%s name=%s ! videoconvert ! avenc_mpeg4 ! rtpmp4vpay name=pay0 )"%(self.name, self.name)
	
        elif self.fmt =='h264':
	    if self.vaapi_enabled is not None:
                pipe = "( intervideosrc channel=%s name=%s ! videoconvert ! vaapipostproc ! vaapiencode_h264 ! rtph264pay name=pay0 pt=96 )"%(self.name, self.name)
	    else:
                pipe = "( intervideosrc channel=%s name=%s ! x264enc tune=zerolatency byte-stream=true ! rtph264pay name=pay0 pt=96 )"%(self.name, self.name)
        return Gst.parse_launch(pipe)


class StreamServer():
    def __init__(self):
        self.server = GstRtspServer.RTSPServer()
        self.server.attach(None)

    def add(self, name):
        m = self.server.get_mount_points()
        m.add_factory("/{0}/h264".format(name),MyFactory('h264', name))


class Finder(object):
    def __init__(self, dev):
        self.caps = None
        self.dev = dev
        self.pipeline = Gst.Pipeline()
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)
        self.src = VirtualDevice(dev['instream'])
        self.vc1 = Gst.ElementFactory.make('videoconvert', None)
        self.video = PlateFinder(dev)
        self.sink = GstOutputStream(dev['outstream'], split=False)

        self.pipeline.add(self.src)
        self.pipeline.add(self.vc1)
        self.pipeline.add(self.video)
        self.pipeline.add(self.sink)
        self.src.link(self.vc1)
        self.vc1.link(self.video)
        self.video.link(self.sink)

    def start(self):
        log.info("starting %s [%s]"%(self.dev['name'], self.dev['instream']))
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        log.info("stopping %s"%self.dev['name'])
        self.pipeline.set_state(gst.STATE_NULL)

    def restart(self):
	log.info('restarting %s'%self.dev['name'])
        self.stop()
        self.start()

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.ERROR: 
            err, debug = message.parse_error()
            error = str(err)
            if debug:
                error += " (%s)"%debug
                log.error("monitor '%s' received error; %s"%(self.dev['name'], error))
	        sleep(10)
	        self.restart()
   	    
        elif t == Gst.MessageType.EOS:
            log.warn('EOS')
            sleep(10)
            self.restart()
	    
        elif t == Gst.MessageType.STATE_CHANGED:
            old, state, pending = message.parse_state_changed()
            if state == Gst.State.NULL:
                log.info("monitor '%s' main pipeline is stopped"% self.dev['name'])
            elif state == Gst.State.PLAYING:
                if message.src == self.pipeline:
                    log.info("'%s' cambio de %s a %s."%(self.dev['name'], self.get_state(old), self.get_state(state))) 
        elif t == Gst.MessageType.APPLICATION and message.has_name('video/x-raw'):
            s = message.get_structure()
            self.caps = s.to_string()
            if self.caps.endswith(';'):
                self.caps = self.caps[:-1]
        elif t == Gst.MessageType.INFO:
            e, d = message.parse_info()
            log.debug("{0}: {1}", e, d)
        elif t == Gst.MessageType.WARNING:
            e, d = message.parse_warning()
            error = str(e)
            if d:
                error += " (%s)"%d
                log.warn("monitor '%s' received warning; %s"%(self.dev['name'], error))
	        sleep(10)
	        self.restart()

    
    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)

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
        self.bus.remove_signal_watch()


class PatchFinder(object):

    def __init__(self, options, pidfile = None):
        self.server = None
        self.mainloop = GObject.MainLoop()
        self.finders = []
        self.options = options
        self.backend = Backend()

        if self.options.debug:
            log.debug(self.options)

    def run(self):
        self.server = StreamServer()
        self.finders = self.setup_monitors()
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            log.warning("Cancelando...")
        finally:
	        self.quit()

    def setup_monitors(self):
        finders = []
        if self.options.all:
	    resp = self.backend.devices()
	    if not resp.error():
            	devs = resp.result
	    else:
		log.error(resp.result)
        else:
            devs = []
            for o in self.options.devices:
                devs.append(self.backend.devices(int(o)))
            
        log.warn('configurando %s dispositivos',len(devs))
        for d in devs:
            f = Finder(d)
            f.start()
            finders.append(f)
            self.server.add(d['outstream'])
        return finders



    def save(self, img, code, stats):
        stats.detected()
        if self.dev.logging:
            log.debug("loging capture to db")
            transaction.begin()
            plate = Plate.findBy(code)
            if plate.active:
                self.src.alarm()
            plate.log()
            transaction.commit()
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        log.save_image(img,code+ts,'log/')
        if img.filename:
            real = path.splitext(path.basename(img.filename))[0].upper()
            output = code.upper().replace(" ","")[:6]
            if output == real[:6]:
                log.debug("\033[92m" + output + ": OK \033[0m")
                stats.found()
            else:
                log.debug(real[:6] + ": " + output)


    def quit(self):
        log.debug('quitting process')
        for m in self.finders:
            m.stop()
        if self.mainloop and self.mainloop.is_running():
           self.mainloop.quit()



if __name__ == "__main__": 
    from optparse import OptionParser
    parser = OptionParser(usage=("%%prog [options]\n"
                                 "Run with no params to watch all enabled devices.\n"
                                 ))
    parser.add_option("-D", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="render debug to buffer and print messages")

    parser.add_option("-A", "--monitor-all",
                      action="store_true", dest="all", default=False,
                      help="Add all enabled devices to be monitored.")

    parser.add_option("-d", "--device",
                      action="append",
                      dest="devices", default=[],
                      help="Add device to monitor  using id.")

    (options, args) = parser.parse_args()
    
    monitor = PatchFinder(options)
    monitor.run()
    
