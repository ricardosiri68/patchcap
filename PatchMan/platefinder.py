#!/usr/bin/env python
import sys
import cv2
import numpy
import gi
from platedetector import PlateDetector
from timeit import default_timer as timer

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
    _caps = "video/x-raw, format=(string){BGR, GRAY8}; video/x-bayer,format=(string){rggb,bggr,grbg,gbrg}"
    _srctemplate = Gst.PadTemplate.new(
        'src',
        Gst.PadDirection.SRC,
        Gst.PadPresence.ALWAYS,
        Gst.Caps.from_string(_caps))

    _sinktemplate = Gst.PadTemplate.new(
        'sink',
        Gst.PadDirection.SINK,
        Gst.PadPresence.ALWAYS,
        Gst.Caps.from_string(_caps))

   
    
    __gsttemplates__ = ( _sinktemplate, _srctemplate)

    def __init__(self):
        GstVideo.VideoFilter.__init__(self)
        self.first = True
        self.analyzer = PlateDetector()
        self.last = None
        self.fc = 0

    def gst_to_cv(self, f, w, h):
        data = f.buffer.extract_dup(0, f.buffer.get_size())
        return  numpy.ndarray((h, w, f.info.finfo.n_components), buffer=data, dtype=numpy.uint8)


    def do_transform_frame_ip(self, f):
        self.fc = self.fc + 1
        c = f.buffer.mini_object.refcount
        f.buffer.mini_object.refcount = 1
        h = f.info.height
        w = f.info.width
        img = self.gst_to_cv(f,w,h)
        img.flags.writeable = True

        if self.fc == 25:
            plate, r = self.analyzer.find2(img)
            if r is not None:
                self.last = r
            self.fc = 0

        if self.last is not None:
            rh, rw = self.last.shape[:2]
            img[h-rh:h,w-rw:w] = self.last

        f.buffer.fill(0, img.tobytes())
        f.buffer.mini_object.refcount = c
        return Gst.FlowReturn.OK

    def do_set_info(self, incaps, in_info, outcaps, out_info):
        print "incaps:", incaps.to_string()
        print "outcaps:", outcaps.to_string()
        return True


def get_element_class(klass):
    element_class = GObject.type_class_peek(klass.__gtype__)
    element_class.__class__ = Gst.ElementClass
    return element_class

get_element_class(PlateFinder).set_metadata('longname', 'classification', 'description', 'author')

def plugin_init(plugin):
    t = GObject.type_register (PlateFinder)
    reg = Gst.Element.register(plugin, "platefinder", 0, t)
    print ('registered', reg)
    return reg

if not Gst.Plugin.register_static(Gst.VERSION_MAJOR, Gst.VERSION_MINOR, "platefinder", "platefinder filter plugin", plugin_init, '0.02', 'LGPL', 'platefinder', 'patchcap', ''):
    print "plugin register failed"
    sys.exit()
