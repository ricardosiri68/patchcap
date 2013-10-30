import os
import Image
import re

class MakeTiff:
	
	__blobsChars = "blobsChars"

	__dirs = os.listdir(__blobsChars)

	__widths = set()

	__sheetWidth = 360

	__numRowOfSheet = 5

	__sheetHight = __numRowOfSheet * 50

	__outputFolder = "training-tiff"

	def __init__(self):
		print "se capturaron: %s caracteres" % len(list(self.getPNGs()))
		self.createSheets();

	def createSheet(self):
		return Image.new("RGB",(self.__sheetWidth,self.__sheetHight),"white")

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
		return self.__sheetWidth//self.getColPx()

	def getColPx(self):
		return max(list(self.getWidths()))

	def sizeRows(self):
		return len(list(self.getPNGs()))//self.sizeCol()

	def rows(self):
		row = [];
		col = 0;
		for png in self.getPNGs():
			if col < self.sizeCol():
				row.append(png)
				col += 1
			else:
				col = 0
				yield row
				row = []

	def insertPNG(self, output, x,y, png):
		print "INSERTING on (%s,%s) %s" % (x,y,png)
		p = Image.open(png)
		output.paste(p,(x,y))

	def insertPNGs(self, rows , output, sheetNum):
		w = self.getColPx()
		y = 0
		for row in rows:
			x = 0
			for png in row:
				self.insertPNG(output, x*w,y*50,png)
				x += 1
			y += 1

	def numSheets(self):
		return len(list(self.rows()))//self.__numRowOfSheet

	def createSheets(self):
		fullRows = list(self.rows())
		for i in range(self.numSheets()):
			output = self.createSheet()
			rows = fullRows[i * self.__numRowOfSheet: (i + 1) * self.__numRowOfSheet]
			print rows
			self.insertPNGs(rows, output,i)
			output.save("%s/%s.png" % (self.__outputFolder,i) )



		

if __name__ == "__main__":
	MakeTiff()
