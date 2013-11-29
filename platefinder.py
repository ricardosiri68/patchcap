from ocr import Ocr
import logging
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
        # cropImg = blob.crop()
        (x,y), w,h = blob.topLeftCorner(),blob.minRectWidth(),blob.minRectHeight()
        margin = 20
        x,y,w,h = x - margin, y - margin, w + (margin*2) , h + (margin*2)
        x = x if x > 0 else 0
        y = y if y > 0 else 0
        w = w if w < img.width else img.width
        h = h if h < img.height else img.height
        
        cropImg = img.crop(x,y, w,h)
        cropImg = self.fixOrientation(cropImg, img.filename, x ,y ,blob)

        return self.findSimbols(cropImg, img.filename)
        
    def fixOrientation(self,cropImg, name, x, y ,blob):
        fixed = ImageBlobWarping(cropImg,blob,x,y,154,50).warped()
        if fixed:
            name = path.splitext(path.basename(name))[0].upper()
            fixed.save("warpped/%s.jpg" % name )
            return fixed
        else:
            return cropImg
       
    def findSimbols(self, img, imgname):
            
        img = img.crop(3,3,img.width-6,img.height-6).resize(h=50)
        img_name = path.splitext(path.basename(imgname))[0].upper()
        if logger.isEnabledFor(logging.DEBUG):
            blobs_folder =  "blobsChars/%s" % img_name
            if not path.isdir(blobs_folder):
                mkdir(blobs_folder)
            imgpath = path.join(blobs_folder,"%s.jpg"%(img_name))
            if path.isfile(imgpath):
                i = 1
                imgpath = path.join(blobs_folder,"%s-%s.jpg"%(img_name,i))
                while path.isfile(imgpath):
                    i += 1
                    imgpath = path.join(blobs_folder,"%s-%s.jpg"%(img_name,i))
            img.save(imgpath) 

        #text = self.ocr.readWord(img.dilate().getBitmap())

        text = self.findChars(img.dilate(), img_name)

        if text:
            return text
        return None

    def findChars(self,img, imgname):

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
                if readed and logger.isEnabledFor(logging.DEBUG):
                    path = "blobsChars/%s/%s-%s.png" % (imgname,readed,i)
                    croped.save(path)
                else:
                    path = "blobsChars/%s/NaN-%s.png" % (imgname,i)
                    croped.save(path)
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

    def prepare(self, img):
        #89/94
        img = (img/3)
        #return (img - img.binarize().morphOpen()).gaussianBlur().binarize()
        return img.binarize().gaussianBlur()


