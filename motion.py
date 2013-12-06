class Motion:
	__prevImg = None
	__threshhold = 5.0
	__frames = 0

	def detect(self, img):
		if self.__prevImg:
			print type(img)
			diff = self.__prevImg - img;
			matrix = diff.getNumpy()
			mean = matrix.mean()
			img.show()
			if mean >= self.__threshhold:
				return img
		else:

			self.__prevImg = img

		self.__frames += 1
		if self.__frames == 15:
			self.__prevImg = img


# from SimpleCV import *

# cam = Camera()
# threshold = 5.0 # if mean exceeds this amount do something

# while True:
#     previous = cam.getImage() #grab a frame
#     time.sleep(0.5) #wait for half a second
#     current = cam.getImage() #grab another frame
#     diff = current - previous
#     matrix = diff.getNumpy()
#     mean = matrix.mean()

#     diff.show()

#     if mean >= threshold:
#             print "Motion Detected"