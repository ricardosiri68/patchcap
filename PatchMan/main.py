#!/usr/bin/env python
import sys
from patchfinder import PatchFinder

from optparse import OptionParser
parser = OptionParser(usage=("%%prog [options] [command]\n"
                                 "Commands: start, stop, restart and nodaemon.\n"
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
 
pf = PatchFinder(options)
pf.run()
