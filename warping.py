from SimpleCV import Display, Color, DrawingLayer
from cv2 import getPerspectiveTransform
import numpy as np

class ImageBlobWarping(object):
	def __init__(self, image,w,h):
		self.__outW = w
		self.__outH = h
		self.__image = image

	def findLines(self):
		lines = self.__image.findLines(70)
		return lines

	def intersections(self):
		lines = self.findLines()
		verticalLines = self.getVerticalLines(lines)
		horizontalLines = self.getHorizontalLines(lines)

		for line in horizontalLines:
			yield self.intersection(line, verticalLines)

	def sortLines(self, lines):
		if len(lines) > 2:
			sortedLines = sorted(lines, key=lambda x: abs(x.points[0][0] - x.points[2][0]) )
			print sortedLines
			return (sortedLines[0],sortedLines[-1])
		elif len(lines) == 2:
			return lines
		else:
			return lines
	def getHorizontalLines(self, lines):
		lines = [l for l in lines if abs(l.angle()) < 45]
		self.sortLines(lines, "CANTIDAD DE LINEAS horizontales INSUFICIENTE !!")

	def getVerticalLines(self, lines):
		lines = [l for l in lines if abs(l.angle()) >= 45]
		self.sortLines(lines, "CANTIDAD DE LINEAS verticales INSUFICIENTE !!")

	def intersection(self, line, lines):
		for l in lines:
			if l != line:
				inter = line.findIntersection(l)
				if inter[0] > 0 and inter[1] > 0:
					yield inter

	def getIntersections(self):
		intersections = set()
		for corners in self.intersections():
			for point in corners:
				intersections.add(point)
		return list(intersections)

	def drawCorners(self):
		corners = self.sortCorners()
		print corners
		i = 0
		for point in corners:
			i += 1
			self.__image.drawText(
				str(i),
				point[0],
				point[1],
				(255,0,0)
				)

	def center(self, points):
		if len(points):
			xAxes = [p[0] for p in points]
			yAxes = [p[1] for p in points]
			return (sum(xAxes) / len(points), sum(yAxes) / len(points))

	def drawCenter(self, center):
		self.__image.dl().circle(center,5)

	def sortCorners(self):
		intersections = self.getIntersections()
		c = self.center(intersections)
		t,b,r = [],[],[]
		if  len(intersections) == 4:
			for p in intersections:
				if(p[1] < c[1]):
					t.append(p)
				else:
					b.append(p)

			print t,b,c
			r.append(t[1] if t[0][0] > t[1][0] else t[0])
			r.append(t[0] if t[0][0] > t[1][0] else t[1])
			r.append(b[0] if b[0][0] > b[1][0] else b[1])
			r.append(b[1] if b[0][0] > b[1][0] else b[0])
			
			return r
		else:
			print "FALLO DE SEGMENTADO: no coincide la cantidad de esquinas"


	def minRect(self):
		intersections = self.getIntersections()
		sortedX = sorted(intersections, key=lambda point: point[0])
		sortedY = sorted(intersections, key=lambda point: point[1])
		return  (
			sortedX[0][0], # x
			sortedY[0][1], # y
			(sortedX[-1][0] - sortedX[0][0]), # width
			(sortedY[-1][1] - sortedY[0][1]) # height
			)

	def warped(self):
		corners = self.sortCorners()
		if corners:
			w,h = self.__outW,self.__outH
			src = np.float32(corners)
			dst = np.float32(((0,0),(w,0),(w,h),(0,h)))
			matrix = getPerspectiveTransform(src,dst)
			out = self.__image.transformPerspective(matrix)
			return out.resize(self.__outH,self.__outW)
		else:
			print "FALLO DE SEGMENTADO: no hay esquinas"

if __name__ == "__main__":

	ibw = ImageBlobWarping()
	dis = Display()
	# ibw.drawCenter(ibw.center(ibw.getIntersections()))
	# ibw.drawCorners()
	# ibw.show(dis)
	warped = ibw.warped()
	warped.save(dis)

	while dis.isNotDone():
		pass
