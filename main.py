from SimpleCV import ImageSet, Display, Color

import time


class PatchFinder:
	def __init__(self,testFolder):
		self.images = ImageSet(testFolder)
		self.display = Display((1024,768))
		self.width = 28.3
		self.heiht = 7.8 
		self.ratios = set()
		self.run()

	def blobs(self,bin):
		blobs = bin.findBlobs()
		if blobs:
			for b in blobs:
				if b.isRectangle():
					if b.area() > 300:
						yield b
	
	def drawBlobs(self, img,blobs):
		for b in blobs:
			self.ratios.add(b.aspectRatio())
			# b.blobImage().save("blobs/%s.jpg" % id(b) )
			b.drawRect(color=Color.RED, width=-1,alpha=128)
			img.drawText(str(b.area()),b.x,b.y + 22,Color.BLUE,20)
			img.drawText(str(b.aspectRatio()),b.x,b.y,Color.GREEN,20)

	def validatePlateBlobs(self, blobs):
		for b in blobs:
			ratio = b.aspectRatio()
			yield ratio > 0.2 and ratio < 5
		

	def findPlate(self, img, thresh=120):
		if thresh > 50:
			bin = img.binarize(thresh)
			img.addDrawingLayer(bin.dl())
			blobs = list(self.blobs(bin))
			if blobs:
				if True in self.validatePlateBlobs(blobs):
					self.drawBlobs(img, blobs)
				else:
					self.findPlate(img,thresh - 10)
			else:
				self.findPlate(img,thresh - 10)


	def run(self):
		for img in self.images:
			self.findPlate(img)
			a = list(self.ratios)
			a.sort()
		
		print a, len(a)
		self.showImages(5)

	def showImages(self, timeout):
		for img in self.images:
			img.save(self.display)
			time.sleep(timeout)

PatchFinder("images/")