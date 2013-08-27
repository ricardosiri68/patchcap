from SimpleCV import ImageSet, Display, Color
import time

class PatchFinder:
	def __init__(self,testFolder):
		self.images = ImageSet(testFolder)
		self.display = Display()
		self.width = 283
		self.heiht = 78 
		self.widths = set()
		self.heights = set()
		self.lengths = set()
		self.ratios = set()
		self.blobs()
		self.showResults()


	def getBlobs(self, img):
		
		return bin

	def blobs(self):
		for img in self.images:

			bin = img.binarize(75)
			bin.morphOpen()
			blobs = bin.findBlobs(-1)
			img.addDrawingLayer(bin.dl())
			img.drawText(img.filename)
			if blobs:
				print img.filename
				for b in blobs:
					if b.isRectangle():
						print b
						b.show()
						self.widths.add(b.width())
						self.heights.add(b.height())
						self.lengths.add(b.length())

		self.images.show(3)



	def showResults(self):
		widths = list(self.widths)
		widths.sort()
		print widths
		print "ANCHO",">"*79
		heights = list(self.heights)
		heights.sort()
		print heights
		print "ALTO",">"*79
		lengths = list(self.lengths)
		lengths.sort()
		print lengths
		print "DENCIDAD",">"*79
		ratios = list(self.ratios)
		ratios.sort()
		print ratios
		print "RATIO",">"*79

	# def run2(self):
	# 	for img in self.images:
	# 		print img.filename

			
pf = PatchFinder("images/")