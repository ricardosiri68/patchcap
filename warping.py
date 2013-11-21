from SimpleCV import Display, Color, DrawingLayer
from cv2 import getPerspectiveTransform
import numpy as np

class ImageBlobWarping(object):
	def __init__(self, image,blob,cropX,cropY,w,h):
		self.__cropX = cropX
		self.__cropY = cropY
		self.__outW = w
		self.__outH = h
		self.__image = image
		self.__blob = blob

	def corners(self):
		return (
			(self.__blob.topLeftCorner()[0] - self.__cropX , self.__blob.topLeftCorner()[1] - self.__cropY ),
			(self.__blob.topRightCorner()[0] - self.__cropX , self.__blob.topRightCorner()[1] - self.__cropY ),
			(self.__blob.bottomRightCorner()[0] - self.__cropX , self.__blob.bottomRightCorner()[1] - self.__cropY ),
			(self.__blob.bottomLeftCorner()[0] - self.__cropX , self.__blob.bottomLeftCorner()[1] - self.__cropY )
			)
	def drawCorners(self):
		corners = self.__blob.minRect()
		if len(corners) == 4:
			for corner in corners:
				self.__image.dl().circle(corner,5,color=(0,255,0))
		else:
			print "NO ES POLIGONO"


	def warped(self):
		corners = self.corners()
		w,h = self.__outW,self.__outH
		src = np.float32(corners)
		dst = np.float32(((0,0),(w,0),(w,h),(0,h)))
		matrix = getPerspectiveTransform(src,dst)
		out = self.__image.transformPerspective(matrix)
		return out

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
