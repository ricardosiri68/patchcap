from ocr import Ocr
import logging
from os import path, mkdir, listdir
from stats import PatchStat
import cv2.cv as cv
from cv2 import copyMakeBorder, BORDER_CONSTANT, getPerspectiveTransform 
from SimpleCV import Color, Image, Camera,JpegStreamer, JpegStreamCamera, VirtualCamera
import numpy as np
logger = logging.getLogger(__name__)

class PlateFinder(object):

    def __init__(self):
        self.ocr = Ocr('spa')

    def find(self,img):
        bin = self.prepare(img)
        blobs = bin.findBlobs(minsize=2000)
       
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

       
    def isPlate(self, plate):
        return len(plate)==6 and \
                len(filter(lambda x: x in '1234567890', list(plate[3:])))==3

        
    def checkBlob(self,img, blob):
        cropImg = blob.crop()
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

                for i in xrange(len(corners)):
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
                #cropImg = cropImg.transformPerspective(getPerspectiveTransform(src,dst))
            
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


        return self.findSimbols(cropImg, img.filename)

       
    def findSimbols(self, img, imgname):
            
        img = img.crop(3,3,img.width-6,img.height-6).resize(h=60)
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


