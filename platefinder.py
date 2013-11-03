from ocr import Ocr
import logging
from os import path, mkdir, listdir
from stats import PatchStat
import cv2.cv as cv
from cv2 import copyMakeBorder, BORDER_CONSTANT 
from SimpleCV import Color, Image, Camera,JpegStreamer, JpegStreamCamera, VirtualCamera

logger = logging.getLogger(__name__)

class PlateFinder(object):

    def __init__(self, stats):
        self.ocr = Ocr('spa')
        self.stats = stats

    def find(self,img):
        plate = self.findPlate(img)
        if plate:
            self.stats.detected()
            if self.isPlate(plate):
                self.stats.found()
        return plate
       
    def isPlate(self, plate):
        return len(plate)==6 and \
                len(filter(lambda x: x in '1234567890', list(plate[3:])))==3

    def findPlate(self, img):
        bin = self.prepare(img)
        blobs = bin.findBlobs(minsize=1000)
       
        if blobs:
            blobs = list((b for b in blobs 
                     if b.isRectangle() and 
                        3 < b.aspectRatio() < 4))
        if blobs:
            for b in blobs:
                plate = self.checkBlob(img,b)
                if plate:
                    return plate
        return None 

    def checkBlob(self,img, blob):
        cropImg = blob.crop()
        if blob.angle()!=0:
            cropImg = cropImg.rotate(blob.angle())
        
        return self.findSimbols(cropImg, img.filename)

    def findSimbols(self, img, imgname):

        img_name = path.splitext(path.basename(imgname))[0].upper()
       
        logger.debug("guardando %s",img_name)
        if logger.isEnabledFor(logging.DEBUG):
            if not path.isdir("blobsChars/%s" % img_name):
                mkdir("blobsChars/%s" % img_name)
            imgpath = "blobsChars/%s/%s.jpg"%(img_name,img_name)
            img = img.crop(3,3,img.width-6,img.height-6).resize(h=50)
            img.save(imgpath) 

        text = self.ocr.readWord(img.dilate().getBitmap())

        #text = self.findChars(img.dilate(), img_name)

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
        con un padding de 20px alrededor
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
        return (img - img.binarize().morphOpen()).gaussianBlur().binarize()


