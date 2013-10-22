import os
import Image
import re

class MakeTiff:
	
	__blobsChars = "blobsChars"

	__dirs = os.listdir(__blobsChars)

	__widths = set()


	def __init__(self):
		self.__output = Image.new("RGB",(1200,self.sizeRows()*50),"white")
		self.insertPNGs();

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
		return 1200//self.getColPx()

	def getColPx(self):
		return max(list(self.getWidths()))

	def sizeRows(self):
		return len(list(self.getPNGs()))//self.sizeCol()

	def rows(self):
		row = [];
		col = 0;
		for png in self.getPNGs():
			if col < 26:
				row.append(png)
				col += 1
			else:
				col = 0
				yield row
				row = []

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
				self.insertPNG(x*w,y*50,png)
				x += 1
			y += 1
		self.__output.save("treaning-tiff.png")



		

if __name__ == "__main__":
	MakeTiff()
