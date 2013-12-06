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