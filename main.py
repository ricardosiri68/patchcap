from SimpleCV import ImageSet, Display, Color, Image

import time, math

class PatchFinder:
	def __init__(self,testFolder):
		self.images = ImageSet(testFolder)
		self.mask = Image("mask/rec.jpg").binarize(100)
		self.display = Display()
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
			print b
		return True

	def findPlate(self, img, thresh=120):
		bin = img.binarize(thresh)
		img.addDrawingLayer(bin.dl())
		blobs = list(self.blobs(bin))
		if blobs:
			if validatePlateBlobs(blobs):
				self.drawBlobs(img, blobs)
		else:
			self.findPlate(img,thresh - 10)


	def run(self):
		for img in self.images:
			self.findPlate(img)
			a = list(self.ratios)
			a.sort()
		
		print a, len(a)
		self.images.show(2)


			
PatchFinder("images/")