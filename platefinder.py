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
        cropImg = blob.crop()
        save_image(cropImg, "antes-orienta")
        cropImg = self.fixOrientation(cropImg, blob)
        save_image(cropImg, "desp-orienta")
        return self.findSimbols(cropImg)

    def fixOrientation(self,cropImg, blob):
        if blob.angle()!=0:
            cropImg = cropImg.rotate(blob.angle())
        try:
            corner_count = 0
            corners=blob.minRect()
            center = blob.centroid()
            r = []
            t = []
            b = []
            src = []
            dst = []
            if corners:
                corner_count = len(corners)

            if corner_count == 4:

                for i in range(len(corners)):
                    c = corners[i]
                    if (c[1] < center[1]):
                        t.append(((float)(c[0]),(float)(c[1])))
                    else:
                        b.append(((float)(c[0]),(float)(c[1])))

                r.append(t[0] if t[0][0]>t[1][0] else t[1])
                r.append(t[1] if t[0][0]>t[1][0] else t[0])
                r.append(b[1] if b[0][0]>b[1][0] else b[0])
                r.append(b[0] if b[0][0]>b[1][0] else b[1])

                src = np.array(r, np.float32)
                w= blob.minRectWidth()
                h= blob.minRectHeight()
                dst = np.array([(0,0), (w,0),(h, w),(0,h)],np.float32)
            #    cropImg = cropImg.transformPerspective(getPerspectiveTransform(src,dst))
                logger.save(cropImg,  "desp-transf") 

        except:
            print "r"
            print r
            print "t"
            print t
            print "src"
            print src
            print "dst"
            print dst
            print r
            print corners
        
        return cropImg        
   

       
    def findSimbols(self, img):
        img = img.crop(3,3,img.width-6,img.height-6).resize(h=50)
        if logger.isEnabledFor(logging.DEBUG):
            save_image(img)
        #text = self.ocr.readWord(img.dilate().getBitmap())
        text = self.findChars(img.dilate())
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

    def prepare(self, img):
        #89/94
        img = (img)
        #return (img - img.binarize().morphOpen()).gaussianBlur().binarize()
        #return img.grayscale().gaussianBlur(window=(5,5),grayscale=True).sobel(1,0,True,3).binarize(10)
        return img.binarize().gaussianBlur()


