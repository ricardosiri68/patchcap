import os
import Image
import re

class MakeTiff:
	
	__blobsChars = "../blobsChars"

	__dirs = os.listdir(__blobsChars)
	__widths = set()


	def __init__(self):
		self.__output = Image.new("RGB",(1200,self.sizeRows()*60),"white")
		print "se capturaron: %s caracteres" % len(list(self.getPNGs()))
		self.insertPNGs();

	def isPNG(self, f):
		return f.split(".")[1].upper() == "PNG"

	def sizeCol(self):
		less = 1  if 1200//self.getColPx() >  1200/self.getColPx() else 0
		return (1200//self.getColPx()) - less

	def getColPx(self):
		return max(list(self.getWidths()))

	def sizeRows(self):
		cantPngs = len(list(self.getPNGs()))
		more = 1  if cantPngs//self.sizeCol() <  cantPngs/float(self.sizeCol()) else 0
		return (cantPngs//self.sizeCol()) + more

	def getPNGs(self):
		for d in self.__dirs:
			f = os.path.join(self.__blobsChars,d)
			yield f

	def getWidths(self):
		for png in self.getPNGs():
			img = Image.open(png)
			self.__widths.add(img.size[0])
		return self.__widths

	def rows(self):
		row = [];
		for png in self.getPNGs():
			row.append(png)
			if len(row) == self.sizeCol():
				yield row
				row = []
		if row:
			yield row

	def insertPNG(self, x,y, png):
		print "INSERTING on (%s,%s) %s" % (x,y,png)
		p = Image.open(png)
		self.__output.paste(p,(x,y))

	def insertPNGs(self):
		w = self.getColPx()
		y = 0
		for row in self.rows():
			x = 0
			for png in row:
				self.insertPNG(x*w,y*60,png)
				x += 1
			y += 1
		self.__output.save("treaning-tiff.png")


if __name__ == "__main__":
	MakeTiff()
