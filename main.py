from SimpleCV import ImageSet, Display, Color
<<<<<<< HEAD
import time
import Image as pilImage
=======
import time, os, logging
>>>>>>> 47d8a3f5e2ba2f5d80d1ed26c8cfe5ba216e661e

class PatchFinder:
    def __init__(self,testFolder):
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)
        #        logging.basicConfig(format='[%(levelname)s]%(asctime)s:%(message)s',level=logging.DEBUG)
        self.images = ImageSet(testFolder)
#        self.display = Display((800,600))
        self.run()

    
    def drawBlobs(self, img,blobs):
        for b in blobs:
            b.drawRect(color=Color.RED, width=-1,alpha=128)
            img.drawText(str(b.area()),b.x,b.y + 22,Color.BLUE,20)
            img.drawText(str(b.aspectRatio()),b.x,b.y,Color.GREEN,20)

    def validatePlateBlobs(self, blobs):
        for b in blobs:
            cropImg = b.crop()
            if (cropImg.height>45): 
                cropImg=cropImg.resize(h=45)

<<<<<<< HEAD
	def validatePlateBlobs(self, img, blobs):
		for b in blobs:
			ratio = b.aspectRatio()
			if ratio > 0.2 and ratio < 5:
				cropImg = img.crop(
					blobs[0].topLeftCorner()[0],
					blobs[0].topLeftCorner()[1],
					b.width(),
					b.height()
					).grayscale()
				if self.findSimbols(cropImg):
					yield b
	
	def findSimbols(self, cropImg):
		if cropImg.width > cropImg.height:
			bin = cropImg.erode().resize(246,110)
			blobs = bin.findBlobs()
			if blobs:
				return True
			else:
				return False
		else:
			return False
=======
            if 3 < b.aspectRatio() < 4 and self.findSimbols(cropImg):
                yield b
>>>>>>> 47d8a3f5e2ba2f5d80d1ed26c8cfe5ba216e661e

    def findSimbols(self, img):
        orc = img.readText()
        if orc and not orc.isspace():
            logging.info("ORC %s",orc)
            return True
        else:
            return False

    def findPlate(self, img):
        bin = (img - img.binarize().morphOpen()).smooth(2).binarize()
#        bin = img.grayscale().binarize().morphOpen().smooth()
        img.addDrawingLayer(bin.dl())
        blobs = list((b for b in bin.findBlobs() if b.isRectangle() and b.area>300))
        if blobs:
            filteredBlobs = list(self.validatePlateBlobs(blobs))
            if len(filteredBlobs):
                self.drawBlobs(img, filteredBlobs)


    def run(self):
        for img in self.images:
            logging.debug("procesando %s",os.path.splitext(os.path.basename(img.filename))[0].upper())
            self.findPlate(img)
            self.saveImage(img)
        
        #self.showImages(5)

<<<<<<< HEAD
	def run(self):
		for img in self.images:
			self.findPlate(img)
			a = list(self.ratios)
			a.sort()
		
		print a, len(a)
                self.showImages(3)
=======
    def showImages(self, timeout):
        for img in self.images:
            img.save(self.display)
            time.sleep(timeout)
>>>>>>> 47d8a3f5e2ba2f5d80d1ed26c8cfe5ba216e661e

    def saveImage(self,i):
        poc_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"test")
        name = os.path.basename(i.filename)
        if not os.path.exists(poc_dir):
            os.makedirs(poc_dir)
        i.save(os.path.join(poc_dir, name))

PatchFinder("images/")
