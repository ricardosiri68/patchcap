#!/usr/bin/env python
from SimpleCV import ImageSet, Display, Color
import time, os, logging
from patchfinder import PatchFinder

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
        poc_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"test")
        name = os.path.basename(i.filename)
        if not os.path.exists(poc_dir):
            os.makedirs(poc_dir)
        i.save(os.path.join(poc_dir, name))
'''


pf = PatchFinder("images/")
pf.run()
