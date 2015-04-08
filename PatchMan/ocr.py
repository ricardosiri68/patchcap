from os import path, environ
import sys
import logging
import ctypes
from string import maketrans
import cv2
from exceptions import IOError
import string



(PSM_OSD_ONLY, PSM_AUTO_OSD, PSM_AUTO_ONLY, PSM_AUTO, PSM_SINGLE_COLUMN,
 PSM_SINGLE_BLOCK_VERT_TEXT, PSM_SINGLE_BLOCK, PSM_SINGLE_LINE,
 PSM_SINGLE_WORD, PSM_CIRCLE_WORD, PSM_SINGLE_CHAR, PSM_SPARSE_TEXT,
 PSM_SPARSE_TEXT_OSD, PSM_COUNT) = map(ctypes.c_int, xrange(14))


# Demo variables
libpath = "/usr/local/lib64/"
TESSDATA_PREFIX = environ.get('TESSDATA_PREFIX')
if not TESSDATA_PREFIX:
    TESSDATA_PREFIX = path.dirname(
                                path.dirname(path.realpath(__file__)))+"/ocr/"

libname = libpath + "libtesseract.so"
libname_alt = "libtesseract.so.3"


class _TessBaseAPI(ctypes.Structure):
    pass

TessBaseAPI = ctypes.POINTER(_TessBaseAPI)


class Ocr(object):
    def __init__(self, lang="spa", log = None):
        if log:
            self.logger = log
        else:
            self.logger = logging.getLogger(__name__)

        self.tesseract = ctypes.CDLL(libname)
        self.tesseract.TessBaseAPICreate.restype = TessBaseAPI
        self.tesseract.TessBaseAPIDelete.restype = None  # void
        self.tesseract.TessBaseAPIDelete.argtypes = [TessBaseAPI]
        self.tesseract.TessBaseAPIInit3.argtypes = [TessBaseAPI, ctypes.c_char_p, ctypes.c_char_p]
        self.tesseract.TessBaseAPISetImage.restype = ctypes.c_void_p
        self.tesseract.TessBaseAPISetImage.argtypes = [TessBaseAPI,
                                          ctypes.c_void_p,
                                          ctypes.c_int,
                                          ctypes.c_int,
                                          ctypes.c_int,
                                          ctypes.c_int]

        # self.tesseract.TessBaseAPISetImage.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.tesseract.TessBaseAPIGetUTF8Text.restype = ctypes.c_char_p
        self.tesseract.TessBaseAPIGetUTF8Text.argtypes = [TessBaseAPI]

        self.api = self.tesseract.TessBaseAPICreate()
        self.rc = self.tesseract.TessBaseAPIInit3(self.api, TESSDATA_PREFIX, lang)

        if (self.rc):
            self.tesseract.TessBaseAPIDelete(self.api)
            self.logger.error("Could not initialize tesseract.\n")
            exit(3)

        self.tesseract.TessBaseAPISetVariable(self.api, "tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.tesseract.TessBaseAPISetPageSegMode(self.api, PSM_SINGLE_CHAR)
        self.reset()

    def __del__(self):
        self.reset()

    def reset(self):
        self.confidence = []
        self.plate = ''
        self.image = None

    def text(self):
        return self.plate

    def read_text(self, image):
        return self.__readChar(image, is_digit=False)

    def read_digit(self, image):
        return self.__readChar(image, is_digit=True)

    def __readChar(self, path, is_digit=False):
        if is_digit:
            self.tesseract.TessBaseAPISetVariable(self.api, "tessedit_char_whitelist", string.digits)
            self.tesseract.TessBaseAPISetVariable(self.api, "tessedit_char_blacklist", string.ascii_uppercase)
        else:
            self.tesseract.TessBaseAPISetVariable(self.api, "tessedit_char_blacklist", string.digits)
            self.tesseract.TessBaseAPISetVariable(self.api, "tessedit_char_whitelist", string.ascii_uppercase)
        
	    self.tesseract.TessBaseAPISetPageSegMode(self.api, PSM_SINGLE_CHAR)
        try:
            self.__loadImage(path)
            text_out = self.tesseract.TessBaseAPIGetUTF8Text(self.api)
            text = ctypes.string_at(text_out)
            c = self.__fix(text.strip(), is_digit)
            self.image = None
        except IOError:
            self.logger.error("Error cargando imagen %s", path, exc_info=1)
            c = None
        except:
            self.logger.error("Error leyendo caracter de %s", path, exc_info=1)
            c = None
        if c:
            self.confidence.append(self.tesseract.TessBaseAPIMeanTextConf(self.api))
            self.plate += c
        return c

    def read_word(self, img):
        self.tesseract.TessBaseAPISetPageSegMode(self.api, PSM_AUTO)
        self.__loadImage(img)
        text_out = self.tesseract.TessBaseAPIGetUTF8Text(self.api)
        text = ctypes.string_at(text_out)
        return text.strip().replace(' ','')

    def confidence(self):
        return self.tesseract.TessBaseAPIMeanTextConf(self.api)

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
        if is_path and not path.isfile(img):
            raise IOError("File %s not found" % (img))
        try:
            if is_path:
                self.image = cv2.imread(img, cv.CV_LOAD_IMAGE_UNCHANGED)
            else:
                self.image = img
            if len(self.image.shape)==3:
                h, w, d = self.image.shape
            else:
                h, w = self.image.shape
                d = 1
            self.tesseract.TessBaseAPISetImage(self.api, self.image.ctypes, w, h, d, w * d)
            return True
        except Exception as e:
            self.logger.error("Error seteando imagen a tesseract: %s", e)
            return False

    def version(self):
        self.tesseract.TessVersion.restype = ctypes.c_char_p
        tesseract_version = self.tesseract.TessVersion()[:4]
        return ("Found tesseract-ocr library version %s." % tesseract_version)


if __name__ == "__main__":
    ocr = Ocr()
    print ocr.version()
    if len(sys.argv) >= 2:
    	img_path =  sys.argv[1]
	print ocr.read_word(img_path)
