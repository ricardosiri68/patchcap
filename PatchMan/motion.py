'''
este modulo se encarga de detectar el movimiento restando las diferencias entre
los frames y evaluando un cambio significativo en la imagen bajo un umbral
superior al 5.0 %
'''


class Motion:
    '''
    clase encargada de detectar movimiento
    '''
    __prevImg = None
    __threshhold = 5.0
    __frames = 0

    def detect(self, img):

        if not self.__prevImg:
		self.__prevImg = img
		return True

        diff = self.__prevImg - img
        matrix = diff.getNumpy()
        mean = matrix.mean()
       	return mean >= self.__threshhold
