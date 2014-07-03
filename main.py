#!/usr/bin/env python
import sys
from patchfinder import PatchFinder

<<<<<<< HEAD
if len(sys.argv)>=2:
=======
'''
    def drawBlobs(self, img,blobs):
        for b in blobs:
            b.drawRect(color=Color.RED, width=-1,alpha=128)
            img.drawText(str(b.area()),b.x,b.y + 22,Color.BLUE,20)
            img.drawText(str(b.aspectRatio()),b.x,b.y,Color.GREEN,20)

    def showImages(self, timeout):
        for img in self.images:
            img.save(self.display)
            time.sleep(timeout)

    def saveImage(self,i):
        poc_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "test"
        )
        name = os.path.basename(i.filename)
        if not os.path.exists(poc_dir):
            os.makedirs(poc_dir)
        i.save(os.path.join(poc_dir, name))
'''
if len(sys.argv) >= 2:
>>>>>>> 34c450442c652c9aa0faf01933c78cb2ec65e70b
    i = sys.argv[1]
else:
    i = "images/"

log = len(sys.argv) == 3 and sys.argv[2]

pf = PatchFinder(i, log)
pf.run()
