#!/usr/bin/env python
import cv2
import logging
import sys
import numpy
import gi
from device import VirtualDevice
from platedetector import PlateDetector
from timeit import default_timer as timer
from log import log_image

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GstVideo, GLib

GObject.threads_init()
Gst.init(None)

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

    def __init__(self):
        GstVideo.VideoFilter.__init__(self)
        self.first = True
        self.analyzer = PlateDetector()
        self.last = None
            
    def do_set_info(self, incaps, in_info, outcaps, out_info):
        if in_info.finfo.format == GstVideo.VideoFormat.I420:
            self.gst_to_cv = self.i420_to_cv
            self.cv_to_gst = self.cv_to_i420
        elif in_info.finfo.format ==  GstVideo.VideoFormat.BGR:
            self.gst_to_cv = self.bgr_to_cv
            self.cv_to_gst = self.cv_to_bgr
        else:
            return False
        logging.debug('in c ' + incaps.to_string()) 
        logging.debug('out c ' + outcaps.to_string()) 
        return True

    def cv_to_bgr(self, img):
        return img

    def bgr_to_cv(self, f, w, h):
        data = f.buffer.extract_dup(0, f.buffer.get_size())
        return numpy.ndarray((h, w, f.info.finfo.n_components), buffer=data, dtype=numpy.uint8)

    def cv_to_i420(self,img):
        yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        (y,u,v) = cv2.split(yuv)
        udown = cv2.pyrDown(u)
        vdown = cv2.pyrDown(v)
        return numpy.concatenate((y,u,v))

        
    def i420_to_cv(self, f, w, h):
        data = f.buffer.extract_dup(0, f.buffer.get_size())
        stream = numpy.fromstring(data,numpy.uint8)
        size = w*h
        print stream.size
        y = stream[0:size].reshape(h,w)
        u = stream[size:(size+(size/4))].reshape((h/2),(w/2))# create the u channel its size=framesize/4
        u_upsize = cv2.pyrUp(u)
        v = stream[(size+(size/4)):].reshape((h/2),(w/2))
        v_upsize= cv2.pyrUp(v)
        yuv = cv2.merge((y,v_upsize,u_upsize))
        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        return bgr


    def do_transform_frame_ip(self, f):
        VirtualDevice.vd[f.buffer.pts] = timer()-VirtualDevice.gt[f.buffer.pts]
        logging.debug('[%s] vc1: %s',f.buffer.pts, VirtualDevice.vd[f.buffer.pts])
        i = timer()

        h = f.info.height
        w = f.info.width
        img = self.gst_to_cv(f,w,h)
        img.flags.writeable = True

        plate, r = self.analyzer.find2(img)
        if r is not None:
            self.last = r
            log_image(img, f.buffer.pts)

        if self.last is not None:
            rh, rw = self.last.shape[:2]
            img[h-rh:h,w-rw:w] = self.last

        f.buffer.fill(0, self.cv_to_gst(img).tobytes())

        pt = timer()-i
        logging.debug('[%s] ana: %s',f.buffer.pts, pt )
        VirtualDevice.vd[f.buffer.pts] = VirtualDevice.vd[f.buffer.pts] + pt

        return Gst.FlowReturn.OK


def plugin_init(plugin):
    t = GObject.type_register (PlateFinder)
    reg = Gst.Element.register(plugin, "platefinder", 0, t)
    print('registered', reg)
    return reg

if not Gst.Plugin.register_static(Gst.VERSION_MAJOR, Gst.VERSION_MINOR, "platefinder", "platefinder filter plugin", plugin_init, '0.02', 'LGPL', 'platefinder', 'patchcap', ''):
    print("plugin register failed")
    sys.exit()
