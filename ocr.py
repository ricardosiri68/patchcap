import os
import logging
import tesseract
from string import maketrans
import cv2.cv as cv
from exceptions import IOError

logger = logging.getLogger(__name__)


class Ocr(object):
    '''
    la clase es la encargada de parchear los objetos obtenidos por el
    reconocimiento de caracteres
    '''

    def __init__(self, lang="spa"):
        self.api = tesseract.TessBaseAPI()
        self.api.Init(".", lang, tesseract.OEM_DEFAULT)
        self.api.SetVariable(
            "tessedit_char_whitelist",
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        self.api.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)
        self.reset()

    def __del__(self):
        self.reset()

    def reset(self):
        self.confidence = []
        self.plate = ''
        self.image = None

    def text(self):
        return self.plate

    def readText(self, image):
        return self.__readChar(image, is_digit=False)

    def readDigit(self, image):
        return self.__readChar(image, is_digit=True)

    def __readChar(self, path, is_digit=False):
        '''
        if is_digit:
            self.api.SetVariable(
            "tessedit_char_whitelist",
            string.digits
            )
            self.api.SetVariable("tessedit_char_blacklist",
            string.ascii_uppercase
            )
        else:
            self.api.SetVariable(
            "tessedit_char_whitelist",
            string.ascii_uppercasei
            )
            self.api.SetVariable("tessedit_char_blacklist", string.digits)
        '''
        self.api.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)
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
            self.plate += c
        return c

    def readWord(self, img):
        self.api = tesseract.TessBaseAPI()
        self.api.Init(".", "spa", tesseract.OEM_DEFAULT)
        self.api.SetVariable(
            "tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        self.api.SetPageSegMode(tesseract.PSM_AUTO)
        self.__loadImage(img)
        return self.api.GetUTF8Text()

    def getConfidence(self):
        return self.api.MeanConf()

    def __fix(self, c, is_digit):
        tab1 = "00011245688"
        tab2 = "ODQIJZASGBX"

        if is_digit:
            tab = maketrans(tab2, tab1)
        else:
            tab = maketrans(tab1, tab2)
        if not c:
            return None

        return c.strip().translate(tab)

    def __loadImage(self, img):
        is_path = isinstance(img, basestring)
        if is_path and not os.path.isfile(img):
            raise IOError("File %s not found" % (img))
        try:
            if is_path:
                self.image = cv.LoadImage(img, cv.CV_LOAD_IMAGE_UNCHANGED)
            else:
                self.image = cv.GetImage(img)
            tesseract.SetCvImage(self.image, self.api)
            return True
        except:
            logger.error("Error seteando imagen a tesseract: %s", img)
            return False
