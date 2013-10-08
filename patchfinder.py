#!/usr/bin/env python
from SimpleCV import ImageSet, Display, Color, Image
from daemon import Daemon
import os, sys, time, datetime, logging
import uuid
from models import *
import string
import tesseract
import cv2



class PatchFinder(Daemon):
    def __init__(self,testFolder):
        super(PatchFinder,self).__init__(
                "/tmp/patchfinder.pid", 
                stdin = sys.stdin, 
                stdout=sys.stdout, 
                stderr=sys.stderr)
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)
        self.images = ImageSet(testFolder)
        logging.info("Iniciando aplicacion")

    def run(self, i=None):
        detected = 0
        if i is not None:
            self.images = ImageSet()
            self.images.append(Image(i))

        for img in self.images:
            # el valor de control del numero de patente esta alojado en el
            # nombre del archivo
            
            real = os.path.splitext(os.path.basename(img.filename))[0].upper()
            
            plate = self.findPlate(img)
            if plate:
                output = plate.upper().replace(" ","")[:6]
                if output == real[:6]:
                    detected+=1
                self.log(plate)
        logging.debug("Detectadas correctamente %d/%d", detected, len(self.images))

    
    def findPlate(self, img):
        bin = self.preProcess(img)
        blobs = list((b for b in bin.findBlobs(minsize=1000) if b.isRectangle() and b.area()>1000 and 3 < b.aspectRatio() < 4))
        if not blobs:
            return False

        for b in blobs:
            cropImg = b.crop()
            if b.angle()!=0:
                cropImg = cropImg.rotate(b.angle())

            plate = self.findSimbols(cropImg, img.filename)
            if plate:
                return plate

    def findSimbols(self, img, imgname):

        imgname = os.path.splitext(os.path.basename(imgname))[0].upper()
        
        orc = self.findInnerChars(img, imgname)

        path = "blobsChars/%s/%s.png"%(imgname,imgname)
        img.crop(3,3,img.width-6,img.height-6).resize(h=42).save(path) 

        if orc:
            logging.debug(imgname[:6]+": "+orc)
            return orc.strip()
        return False

    def findInnerChars(self,img, imgname):
        '''
        busca 6 o mas blobs dentro de la patente y evalua sus caracteres uno por uno
        los genera y luego findSimbols los lista y los agrupa en un string
        '''


        inv = img.invert()
        blobs = inv.findBlobs()
        if blobs and len(blobs) >= 6:
            if not os.path.isdir("blobsChars/%s" % imgname):
                os.mkdir("blobsChars/%s" % imgname)
            chars=''
            i = 0
            conf = []
            tess = tesseract.TessBaseAPI()

            for b in sorted(blobs, key=lambda b: b.minX()) : 
                aspectRatio = float(float(b.height())/float(b.width()))
                if not 1.75<=aspectRatio<=3: continue
                croped =  self.cropInnerChar(b,img)
                letter_path = "blobsChars/%s/%s.png" % (imgname,imgname[i]) 
                croped.save(letter_path)
                tess.Init(".","eng",tesseract.OEM_DEFAULT)
                if (i>2):
                    tess.SetVariable("tessedit_char_whitelist", string.digits )
                    tess.SetVariable("tessedit_char_blacklist", string.ascii_uppercase)
                else:
                    tess.SetVariable("tessedit_char_whitelist", string.ascii_uppercase)
                    tess.SetVariable("tessedit_char_blacklist", string.digits )
                
                tess.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)
                tesseract.ProcessPagesRaw(letter_path,tess)
                char=tess.GetUTF8Text().strip()
                if char:
                    chars +=char
                conf.append(tess.MeanTextConf())
                i += 1
            #logging.debug(conf)
            return chars
        
    def cropInnerChar(self,blob, img):
        '''
        corta los blobs que se encuentran dentro del blob de la patente
        con un padding de 20px alrededor
        '''
        
        new_img = Image(cv2.copyMakeBorder(blob.crop().getNumpyCv2(),15,15,15,15,cv2.BORDER_CONSTANT, value=Color.BLACK), cv2image=True).rotate90()
        return new_img.resize(h=50).invert().smooth()
       
    
    def preProcess(self, img):
        return (img - img.binarize().morphOpen()).gaussianBlur().binarize()



    def log(self, plate):
        dt =datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        #logging.info("[%s] %s", dt, plate)
        #TODO: guardar en db


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

