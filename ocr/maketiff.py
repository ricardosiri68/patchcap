import os
import Image
import re

class MakeTiff:
	
	__blobsChars = "../blobsChars"

	__dirs = os.listdir(__blobsChars)

	__widths = set()

	__sheetWidth = 360

	__numRowOfSheet = 5

	__sheetHight = __numRowOfSheet * 60

	__outputFolder = "training-tiff"

	def __init__(self):
		print "SE CAPTURARON: %s CARACTERES" % len(list(self.getPNGs()))
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
		cantPNGs = len(list(self.getPNGs()))
		sizeCol = self.sizeCol()
		more  = 1 if ( cantPNGs//sizeCol < cantPNGs/sizeCol) else 0
		return (cantPNGs//sizeCol) + more

	def rows(self):
		row = [];
		for png in self.getPNGs():
			row.append(png)
			if len(row) == self.sizeCol():
				yield row
				row = []
		if row:
			yield row

	def insertPNG(self, output, x,y, png):
		print "INSERTING on (%s,%s) %s" % (x,y,png)
		p = Image.open(png)
		output.paste(p,(x,y))

	def insertPNGs(self, rows , output):
		w = self.getColPx()
		y = 0
		for row in rows:
			x = 0
			for png in row:
				self.insertPNG(output, x*w,y*60,png)
				x += 1
			y += 1

	def numSheets(self):
		cantRows = len(list(self.rows()))
		more = 1 if cantRows//self.__numRowOfSheet < cantRows/self.__numRowOfSheet else 0
		return (cantRows//self.__numRowOfSheet) + more

	def createSheets(self):
		fullRows = list(self.rows())
		numSheet = self.numSheets()
		print "CANTIDAD DE HOJAS: %s" % numSheet
		for i in range(numSheet + 1):
			output = self.createSheet()
			rows = fullRows[i * self.__numRowOfSheet: (i + 1) * self.__numRowOfSheet]
			self.insertPNGs(rows, output)
			output.save("%s/%s.png" % (self.__outputFolder,i) )



		

if __name__ == "__main__":
	MakeTiff()
