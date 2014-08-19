#!/usr/bin/env python
import sys
from patchfinder import PatchFinder

if len(sys.argv) >= 2:
    i = sys.argv[1]
else:
    i = "../images/"

log = len(sys.argv) == 3 and sys.argv[2]

pf = PatchFinder(i, log)
pf.run()
