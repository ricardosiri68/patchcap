import os
import Image
import re

class MakeTiff:
	
	__blobsChars = "blobsChars"

	__dirs = os.listdir(__blobsChars)

	__widths = set()


	def __init__(self):
		self.__output = Image.new("RGB",(1200,self.sizeRows()*50))

	def isPNG(self, f):
		return f.split(".")[1].upper() == "PNG"

	def getPNGs(self):
		for d in self.__dirs:
			directory = "%s/%s" % (self.__blobsChars,d)
			for f in os.listdir(directory):
				if self.isPNG(f):
					yield "%s/%s" % (directory,f)

	def getWidths(self):
		for png in self.getPNGs():
			img = Image.open(png)
			self.__widths.add(img.size[0])
		return self.__widths

	def sizeCol(self):
		return 1200//max(list(self.getWidths()))

	def sizeRows(self):
		return len(list(self.getPNGs()))//self.sizeCol()

	def getRowList(self):



if __name__ == "__main__":
	MakeTiff()
