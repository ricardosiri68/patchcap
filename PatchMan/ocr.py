import os
import logging
import ctypes
from string import maketrans
import cv2.cv as cv
from exceptions import IOError

logger = logging.getLogger(__name__)

# Demo variables
libpath = "/usr/local/lib64/"
TESSDATA_PREFIX = os.environ.get('TESSDATA_PREFIX')
if not TESSDATA_PREFIX:
    TESSDATA_PREFIX = "../"

libname = libpath + "libtesseract.so"
libname_alt = "libtesseract.so.3"


class Ocr(object):
    '''
    la clase es la encargada de parchear los objetos obtenidos por el
    reconocimiento de caracteres
    '''

    def __init__(self, lang="spa"):
        self.tesseract = ctypes.cdll.LoadLibrary(libname)
        self.api = self.tesseract.TessBaseAPICreate()
        self.rc = self.tesseract.TessBaseAPIInit3(self.api, TESSDATA_PREFIX, lang);


        if (self.rc):
            self.tesseract.TessBaseAPIDelete(self.api)
            logger.error("Could not initialize tesseract.\n")
            exit(3)

        self.api.TessBaseAPISetVariable(
            "tessedit_char_whitelist",
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        self.api.TessBaseAPISetPageSegMode(self.tesseract.PSM_SINGLE_CHAR)
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
        self.api.TessBaseAPISetPageSegMode(self.tesseract.PSM_SINGLE_CHAR)
        try:
            self.__loadImage(path)
            text = self.tesseract.TessBaseAPIGetUTF8Text(self.api)
            c = self.__fix(text.strip().decode('utf-8'), is_digit)
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
     
        self.api.TessBaseAPISetPageSegMode(tesseract.PSM_AUTO)
        self.__loadImage(img)
        return self.api.TessBaseAPIGetUTF8Text()

    def getConfidence(self):
        return self.api.TessBaseAPIMeanTextConf()

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
            h, w, d = self.image.shape
            self.tesseract.TessBaseAPISetImage(self.api, self.image.ctypes, w, h, d, w * d)
            return True
        except:
            logger.error("Error seteando imagen a tesseract: %s", img)
            return False

    def version(self):
        self.tesseract.TessVersion.restype = ctypes.c_char_p
        tesseract_version = self.tesseract.TessVersion()[:4]
        return ("Found tesseract-ocr library version %s." % tesseract_version)


if __name__ == "__main__":
    ocr = Ocr()
    print ocr.version()
    