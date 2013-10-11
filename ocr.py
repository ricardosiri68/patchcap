import os, logging
import tesseract
from string import maketrans
import cv2.cv as cv
from exceptions import IOError
logger = logging.getLogger(__name__)

class Ocr(object):

    def __init__(self, lang = "eng"):
        self.api = tesseract.TessBaseAPI()
        self.api.Init(".",lang,tesseract.OEM_DEFAULT)
        self.api.SetVariable("tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.api.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)
        self.reset()

    def reset(self):
        self.confidence = []
        self.plate = ''
        self.image = None

    def text(self):
        return self.plate

    def readText(self, image):
       return self.__readChar(image, is_digit = False) 

    def readDigit(self, image):
       return self.__readChar(image, is_digit = True) 
    
    def __readChar(self,path, is_digit = False):
        '''
        if is_digit:
            self.api.SetVariable("tessedit_char_whitelist", string.digits)
            self.api.SetVariable("tessedit_char_blacklist", string.ascii_uppercase)
        else:
            self.api.SetVariable("tessedit_char_whitelist", string.ascii_uppercase)
            self.api.SetVariable("tessedit_char_blacklist", string.digits) 
        '''
        try:
            self.__loadImage(path)
            c = self.__fix(self.api.GetUTF8Text(), is_digit)
            self.image = None
        except IOError:
            logger.error("Error cargando imagen %s", path, exc_info=1)
            c = None
        except:
            logger.error("Error leyendo caracter de %s", path, exc_info=1)
            c = None 
        if c:
            self.confidence.append(self.api.MeanTextConf())
            self.plate +=c
        return c 


    def getConfidence(self):
        return self.api.MeanConf()

    def __fix(self,c, is_digit):
        tab1 = "001124568"
        tab2 ="ODIJZASGB"
        
        if is_digit:
            tab = maketrans(tab2, tab1)
        else:
            tab = maketrans(tab1, tab2)
        if not c:
            return None
        return c.strip().translate(tab)

    def __loadImage(self, path):
        if not os.path.isfile(path):
            raise IOError("File %s not found"%(path))
        try:
            self.image = cv.LoadImage(path, cv.CV_LOAD_IMAGE_UNCHANGED)
            tesseract.SetCvImage(self.image,self.api)
            return True 
        except:
            logger.error("Error seteando imagen a tesseract: %s",path)
            return False

