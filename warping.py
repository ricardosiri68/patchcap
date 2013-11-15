from SimpleCV import Display, Color, DrawingLayer
from cv2 import getPerspectiveTransform
import numpy as np

class ImageBlobWarping(object):
	def __init__(self, image):
		self.__image = image

	def findLines(self):
		lines = self.__image.findLines(70)
		return lines

	def intersections(self):
		lines = self.findLines()
		for line in lines:
			yield self.intersection(line, lines)
		

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
			w,h = 300,220
			src = np.float32(corners)
			dst = np.float32(((0,0),(w,0),(w,h),(0,h)))
			matrix = getPerspectiveTransform(src,dst)
			out = self.__image.transformPerspective(matrix)
			return out.resize(220,300)
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
