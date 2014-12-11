#!/usr/bin/env python
import sys
import cv2.cv as cv
import tesseract

if len(sys.argv) >= 2:
    i = sys.argv[1]
else:
    i = "letras.jpg"

image=cv.LoadImage(i, cv.CV_LOAD_IMAGE_GRAYSCALE)

api = tesseract.TessBaseAPI()
api.Init(".","eng",tesseract.OEM_DEFAULT)
#api.SetPageSegMode(tesseract.PSM_SINGLE_WORD)
api.SetPageSegMode(tesseract.PSM_AUTO)
tesseract.SetCvImage(image,api)
text=api.GetUTF8Text()
conf=api.MeanTextConf()
print text
