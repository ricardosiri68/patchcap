#!/usr/bin/env python
import cv2
import logging
import sys
import numpy
import gi
import time
import datetime
from device import VirtualDevice
from platedetector import PlateDetector
from timeit import default_timer as timer

from log import ImageLogger
import multiprocessing
from multiprocessing import Manager, Process, Queue
from Queue import Empty

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GstVideo, GLib

GObject.threads_init()
Gst.init(None)

def analyze(src, dst, log, roi):
    detector  = PlateDetector()
    while True:
        img, ts = src.get()
        if img is None: return
        if roi is None:
            roi = [0,0,img.shape[1], img.shape[0]]
        try: 
            plate, r = detector.find2(img[roi[1]:roi[3], roi[0]:roi[2]])
            if r is not None:
                pr = [r[0]+roi[0], r[1]+roi[1], r[2], r[3]]
                dst.put((plate,pr, img, ts))
                log.image(img, datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S'))
        except Exception as e:
            logging.debug(roi)
            logging.error(e, exc_info=True)



class PlateFinder(GstVideo.VideoFilter):
    __gstmetadata__ = (
        "PlateFinder plugin",
        "newelement",
        "Description",
        "Contact")
    _srccaps = "video/x-raw, format={I420, BGR}"
    _sinkcaps = "video/x-raw, format={I420}"
    _srctemplate = Gst.PadTemplate.new(
        'src',
        Gst.PadDirection.SRC,
        Gst.PadPresence.ALWAYS,
        Gst.Caps.from_string(_srccaps))

    _sinktemplate = Gst.PadTemplate.new(
        'sink',
        Gst.PadDirection.SINK,
        Gst.PadPresence.ALWAYS,
        Gst.Caps.from_string(_sinkcaps))

    __gsttemplates__ = (_sinktemplate, _srctemplate)

    def __init__(self, dev):
        GstVideo.VideoFilter.__init__(self)
        self.last = None
        manager = Manager()
        self.procs = multiprocessing.cpu_count() * 2
        self.src = multiprocessing.Queue()
        self.dst = multiprocessing.Queue()
        self.log = ImageLogger(dev.id)
        if dev.roi is not None:
            self.roi = map(int, dev.roi.split(","))
        else:
            self.roi = None

    def do_start(self):
        for _ in range(self.procs): multiprocessing.Process(target=analyze, args=(self.src, self.dst, self.log, self.roi)).start()
        return True

    def do_stop(self):
        for _ in range(self.procs):
            self.src.put((None, None))
        return True

    def do_set_info(self, incaps, in_info, outcaps, out_info):
        if in_info.finfo.format == GstVideo.VideoFormat.I420:
            self.gst_to_cv = self.i420_to_cv
            self.cv_to_gst = self.cv_to_i420
        elif in_info.finfo.format ==  GstVideo.VideoFormat.BGR:
            self.gst_to_cv = self.bgr_to_cv
            self.cv_to_gst = self.cv_to_bgr
        else:
            return False
        return True

    def cv_to_bgr(self, img):
        return img

    def bgr_to_cv(self, f, w, h):
        data = f.buffer.extract_dup(0, f.buffer.get_size())
        return numpy.ndarray((h, w, f.info.finfo.n_components), buffer=data, dtype=numpy.uint8)

    def cv_to_i420(self,img):
        yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)
        return yuv

    def i420_to_cv(self, f, w, h):
        data = f.buffer.extract_dup(0, f.buffer.get_size())
        yuv = numpy.ndarray((h*3/2,w,1), buffer=data, dtype=numpy.uint8)
        st = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_IYUV)
        return st

    def do_transform_frame_ip(self, f):
        h = f.info.height
        w = f.info.width
        img = self.gst_to_cv(f,w,h)
        self.src.put((img.copy(), time.time()))

        while not self.dst.empty():
            (plate, (x,y,w,h), orig_img, ts)  = self.dst.get()
            self.last = orig_img[y:y+h,x:x+w]

        if self.last is not None:
            img.flags.writeable = True
            rh, rw = self.last.shape[:2]
            img[h-rh:h,w-rw:w] = self.last
            f.buffer.fill(0, self.cv_to_gst(img).tobytes())
        return Gst.FlowReturn.OK



def plugin_init(plugin):
    t = GObject.type_register (PlateFinder)
    return Gst.Element.register(plugin, "platefinder", 0, t)

if not Gst.Plugin.register_static(Gst.VERSION_MAJOR, Gst.VERSION_MINOR, "platefinder", "platefinder filter plugin", plugin_init, '0.02', 'LGPL', 'platefinder', 'patchcap', ''):
    print("plugin register failed")
    sys.exit()
