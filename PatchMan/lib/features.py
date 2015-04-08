import cv2
 
class RGBHistogram:
     def __init__(self, bins):
         self.bins = bins
          
          def get(self, img):
              hist = cv2.calcHist([img], [0, 1, 2],
                      None, self.bins, [0, 256, 0, 256, 0, 256])
              hist = cv2.normalize(hist)
              return hist.flatten()


class HuMoments:
    def get(self, img):
        return cv2.HuMoments(cv2.moments(img)).flatten()
