from ocr import Ocr
import logging
from log import save_image
from os import path, mkdir, listdir
from stats import PatchStat
import cv2.cv as cv
from cv2 import copyMakeBorder, BORDER_CONSTANT, getPerspectiveTransform 
from SimpleCV import Color, Image, Camera,JpegStreamer, JpegStreamCamera, VirtualCamera
import numpy as np
from warping import ImageBlobWarping
logger = logging.getLogger(__name__)

class PlateFinder(object):

    def __init__(self):
        self.ocr = Ocr('spa')

    def find(self,img):
        bin = self.prepare(img)
        blobs = bin.findBlobs(minsize=1000)
       
        if blobs:
            blobs = list((b for b in blobs if 3 < b.aspectRatio() < 4))
        if blobs:
            for b in blobs:
                plate = self.checkBlob(img,b)
                if plate:
                    return plate
        return None 

    def checkBlob(self, img, blob):

        (x,y), w,h = blob.topLeftCorner(),blob.minRectWidth(),blob.minRectHeight()
        margin = 20
        x,y,w,h = x - margin, y - margin, w + (margin*2) , h + (margin*2)
        x = x if x > 0 else 0
        y = y if y > 0 else 0
        w = w if w < img.width else img.width
        h = h if h < img.height else img.height
        
        cropImg = img.crop(x,y, w,h)
        cropImg.filename = img.filename
        save_image(cropImg, "antes-orienta")
        cropImg = self.fixOrientation(cropImg, x ,y ,blob)
        cropImg.filename = img.filename
        save_image(cropImg, "desp-orienta")
        cropImg = self.prepare(cropImg, False)
        cropImg.filename = img.filename
        return self.findSimbols(cropImg)


    def fixOrientation(self,cropImg, x, y ,blob):
        fixed = ImageBlobWarping(cropImg,blob,x,y,154,50).warped()
        if fixed:
            if blob.angle()!=0:
                fixed = fixed.rotate(blob.angle())
            return fixed
        else:
            return cropImg
       
    def findSimbols(self, srcimg):
        img = srcimg.crop(3,3,srcimg.width-6,srcimg.height-6).resize(h=50).dilate()
        img.filename = srcimg.filename
        if logger.isEnabledFor(logging.DEBUG):
            save_image(img,'antes-findChars')
        #text = self.ocr.readWord(img.dilate().getBitmap())
        img.filename = srcimg.filename
        text = self.findChars(img)
        if text:
            return text
        return None

    def findChars(self,img):

        # busca 6 o mas blobs dentro de la patente y evalua sus caracteres uno por uno
        # los genera y luego findSimbols los lista y los agrupa en un string

        inv = img.invert()
        blobs = inv.findBlobs()
        if blobs and len(blobs) >= 6:
            i = 0
            readed = False
            self.ocr.reset()
            for b in sorted(blobs, key=lambda b: b.minX()) : 
                aspectRatio = float(float(b.height())/float(b.width()))
                if not 1.75<=aspectRatio<=3: continue
                croped =  self.cropInnerChar(b,img)
                ipl_img = croped.getBitmap()
                if (i>2):
                    readed = self.ocr.readDigit(ipl_img)
                else:
                    readed = self.ocr.readText(ipl_img)
                if logger.isEnabledFor(logging.DEBUG):
                    if not readed:
                        readed = 'NaN' 
                    croped.filename = img.filename
                    save_image(croped,"%s-%i" % (readed,i))
                i += 1
            return self.ocr.text()
        
    
    def cropInnerChar(self,blob, img):
        '''
        corta los blobs que se encuentran dentro del blob de la patente
        con un padding de 5px alrededor
        '''

        blobCroped = blob.crop()
         
        new_img = Image(
            copyMakeBorder(
                blobCroped.getNumpyCv2(),
                5,5,5,5,BORDER_CONSTANT, 
                value=Color.BLACK),
            cv2image=True)

        return new_img.invert()

    def prepare(self, img , scale = True):
        #89/94
        if(scale):
            img = (img/3)

        #return (img - img.binarize().morphOpen()).gaussianBlur().binarize()
        #return img.grayscale().gaussianBlur(window=(5,5),grayscale=True).sobel(1,0,True,3).binarize(10)
        return img.binarize().gaussianBlur()