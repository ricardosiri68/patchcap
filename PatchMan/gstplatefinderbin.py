#!/usr/bin/python
from os import path
import gi
import numpy
import logging
from platedetector import PlateDetector
from gi.repository import GObject, Gst, GstVideo

class PlateFinderBin(Gst.Bin):
    __gstdetails__ = (
        'Argentinian Cars License Plate recognizer',
        'Video Filter',
        ('Tries to detect a valid plate in the frame and '
         'overlay a text with the recognized license'),
        'Hernando Rojas <hrojas@lacuatro.com.ar>'
    )

    __gsttemplates__ = (
        Gst.PadTemplate.new(
            'src',
            Gst.PadDirection.SRC,
            Gst.PadPresence.ALWAYS,
            Gst.caps_from_string('video/x-raw(ANY)')
        ),
        Gst.PadTemplate.new(
            'sink',
            Gst.PadDirection.SINK,
            Gst.PadPresence.ALWAYS,
            Gst.caps_from_string('video/x-raw(ANY)')
        ),
    )

    __gproperties__ = {
        'roi': (
            GObject.TYPE_STRING,
            'roi',
            'Region in frame to analyze',
            None,
            GObject.PARAM_READWRITE,
        ),
    }

    def __init__(self):
        super(PlateFinder, self).__init__()
        self.count = 0
        self.ult = ''
        self.analyzer = PlateDetector()
        # Create elements
        tee = Gst.ElementFactory.make('tee', "tee")
        q1 = Gst.ElementFactory.make('queue', None)
        self.text = Gst.ElementFactory.make('textoverlay', 'text')
        q2 = Gst.ElementFactory.make('queue', None)
        convert = Gst.ElementFactory.make('videoconvert', None)
        scale = Gst.ElementFactory.make('videoscale', None)

        appsink = Gst.ElementFactory.make('appsink', 'app')
        appsink.set_property('max-buffers', 100)
        appsink.set_property('sync', False)
        appsink.set_property('emit-signals', True)
        appsink.set_property('drop', True)
        appsink.connect('new-sample', self.on_new_buffer)

        # Add elements to Bin
        self.add(tee)
        self.add(q1)
        self.add(self.text)
        self.add(q2)
        self.add(convert)
        self.add(scale)
        self.add(appsink)

        # scale.set_property('method', 3)  # lanczos, highest quality scaling

        # Link elements
        tee.link(q1)
        q1.link(self.text)
        tee.link(q2)
        q2.link(convert)
        convert.link(scale)
        caps = Gst.caps_from_string((
            "video/x-raw, format=(string){BGR, GRAY8};"
            "video/x-bayer, format=(string){rggb,bggr,grbg,gbrg}"
        ))
        scale.link_filtered(appsink, caps)

        # Add Ghost Pads
        self.add_pad(
            Gst.GhostPad.new('sink', tee.get_static_pad('sink'))
        )
        self.add_pad(
            Gst.GhostPad.new('src', self.text.get_static_pad('src'))
        )

    def gst_to_opencv(self, sample):
        buf = sample.get_buffer()
        caps = sample.get_caps()
        h = caps.get_structure(0).get_value('height')
        w = caps.get_structure(0).get_value('width')
        data = buf.extract_dup(0, buf.get_size())
        img = numpy.ndarray((h, w, 3), buffer=data, dtype=numpy.uint8)
        Glib.free(data)
        return img

    def on_new_buffer(self, appsink):
            try:
                self.count = self.count + 1
                if self.count % 9 <> 0:
                    return Gst.FlowReturn.OK
                sample = appsink.emit('pull-sample')
                img = self.gst_to_opencv(sample)
                plate = self.analyzer.find(img)
            
                if plate and len(plate)>4:
                    self.ult = plate
                    self.text.set_property("text", "Patente: %s" % plate)
                else:
                    self.text.set_property("text",
                            "Frames proc: %s. Ultima: %s" % (self.count, self.ult))
                return Gst.FlowReturn.OK
            except IOError:
                pass

if __name__ == "__main__": 
    loop = GObject.MainLoop()
    GObject.threads_init()
    Gst.init(None)
    Gst.segtrap_set_enabled(False)




