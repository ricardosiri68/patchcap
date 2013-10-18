#!/usr/bin/env python
from SimpleCV import ImageSet, Display, Color, Image
from daemon import Daemon
import os, sys, time, datetime
import logging, logging.config
import uuid
from ocr import Ocr
from models import *
import cv2.cv as cv
from cv2 import copyMakeBorder, BORDER_CONSTANT 
import log

logger = log.setup()

class PatchFinder(Daemon):
    def __init__(self,testFolder):
        super(PatchFinder,self).__init__(
                "/tmp/patchfinder.pid", 
                stdin = sys.stdin, 
                stdout=sys.stdout, 
                stderr=sys.stderr)

        self.images = []
        
        logger.info("Iniciando aplicacion")
        self.ocr = Ocr()
        self.testFolder = testFolder

    def run(self, i=None):
        detected = 0
        if i is not None:
            self.images = []
            self.images.append(i)
        else:
            if self.testFolder:
                for imgfile in os.listdir(self.testFolder):
                    if imgfile.endswith(".jpg"):
                        self.images.append(os.path.join(self.testFolder,imgfile))

        for imgpath in self.images:
            img = Image(imgpath)
            # el valor de control del numero de patente esta alojado en el
            # nombre del archivo
            real = os.path.splitext(os.path.basename(img.filename))[0].upper()
            detected+=self.comparePlate(img)
            
        logger.info("Detectadas correctamente %d/%d", detected, len(self.images))

    def comparePlate(self, img):
        real = os.path.splitext(os.path.basename(img.filename))[0].upper()
        plate = self.findPlate(img)
        if plate:
            output = plate.upper().replace(" ","")[:6]
            self.log(plate)
            if output == real[:6]:
                logger.debug("\033[92m"+output+": OK \033[0m")
                return 1
        return 0
                
    def findPlate(self, img):
        bin = self.preProcess(img)
        blobs = list((b for b in bin.findBlobs(minsize=1000) 
                     if b.isRectangle() and 
                        b.area()>1000 and 
                        3 < b.aspectRatio() < 4))
        if not blobs:
            return False

        for b in blobs:
            plate = self.checkBlob(img,b)
            if plate:
                return plate

    def checkBlob(self,img, blob):
        cropImg = blob.crop()
        if blob.angle()!=0:
            cropImg = cropImg.rotate(blob.angle())
        
        return self.findSimbols(cropImg, img.filename)

    def findSimbols(self, img, imgname):

        img_name = os.path.splitext(os.path.basename(imgname))[0].upper()
        
        if logger.isEnabledFor(logging.DEBUG):
            if not os.path.isdir("blobsChars/%s" % img_name):
                os.mkdir("blobsChars/%s" % img_name)
            path = "blobsChars/%s/%s.jpg"%(img_name,img_name)
            img.crop(3,3,img.width-6,img.height-6).resize(h=42).save(path) 

        text = self.findChars(img, img_name)

        if text:
            logger.debug(img_name[:6]+": "+text)
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
                i += 1
            return self.ocr.text()
        
    
    def cropInnerChar(self,blob, img):
        '''
        corta los blobs que se encuentran dentro del blob de la patente
        con un padding de 20px alrededor
        '''
        new_img = Image(
            copyMakeBorder(
            
                blob.crop().getNumpyCv2(),
                15,15,15,15,BORDER_CONSTANT, 
                value=Color.BLACK),
            
            cv2image=True).rotate90()

        return new_img.resize(h=50).invert().smooth()

    
    def preProcess(self, img):
        return (img - img.binarize().morphOpen()).gaussianBlur().binarize()


    def log(self, plate):
        dt =datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        # logger.info(plate)
        # TODO: guardar en db


if __name__ == "__main__":
    
    daemon = PatchFinder("images/")

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
                daemon.start()
        elif 'stop' == sys.argv[1]:
                daemon.stop()
        elif 'restart' == sys.argv[1]:
                daemon.restart()
        else:
            print "comando desconocido"
            sys.exit(2)
        sys.exit(0)
    else:
        print "uso: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

