#!/usr/bin/env python
from SimpleCV import ImageSet, Display, Color, Image
from daemon import Daemon
import os, sys, time, datetime, logging
import uuid
from models import *
import string
import tesseract
import cv2

tess = tesseract.TessBaseAPI()
tess.Init(".","eng",tesseract.OEM_DEFAULT)
tess.SetVariable("tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
tess.SetVariable("classify_enable_learning", "0")
tess.SetVariable("classify_enable_adaptive_matcher", "0")
tess.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)
 

class PatchFinder(Daemon):
    def __init__(self,testFolder):
        super(PatchFinder,self).__init__(
                "/tmp/patchfinder.pid", stdin = sys.stdin,
                stdout=sys.stdout, stderr=sys.stderr
                )
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
            orig = os.path.splitext(os.path.basename(img.filename))[0].upper()
            logging.debug("procesando %s", orig)
            plate = self.findPlate(img)
            if plate:
                output = plate.upper().replace(" ","")[:6]
                if output == orig[:6]:
                    logging.info ("Detectada OK!")
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

        tess = tesseract.TessBaseAPI()
        tess.Init(".","eng",tesseract.OEM_DEFAULT)
        tess.SetVariable("tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        tess.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)
        path = "blobsChars/%s/%s.jpg"%(imgname,imgname)
        img.crop(3,3,img.width-6,img.height-6).resize(h=42).save(path) 
        tesseract.ProcessPagesRaw(path,tess)
        plate=tess.GetUTF8Text().strip()
        logging.debug("%s: %s"%(imgname, plate))

        if orc:
            logging.debug(orc)
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
            for b in sorted(blobs, key=lambda b: b.minX()) : 
                aspectRatio = float(float(b.height())/float(b.width()))
                if not 1.75<=aspectRatio<=3: continue
                croped =  self.cropInnerChar(b,img)
                letter_path = "blobsChars/%s/%s.jpg" % (imgname,i) 
                croped.save(letter_path)
                tesseract.ProcessPagesRaw(letter_path,tess)
                if (i>2):
                    tess.SetVariable("tessedit_char_whitelist", string.digits )
                #    tess.SetVariable("tessedit_char_blacklist", string.ascii_uppercase)
                else:
                    tess.SetVariable("tessedit_char_whitelist", string.ascii_uppercase)
                 #   tess.SetVariable("tessedit_char_blacklist", string.digits )
                char=tess.GetUTF8Text().strip()
                if char:
                    chars +=char
                conf.append(tess.MeanTextConf())
                i += 1
            logging.debug(conf)
            return chars
        
    def cropInnerChar(self,blob, img):
        '''
        corta los blobs que se encuentran dentro del crop de la patente
        con un padding de 3px o menos
        '''
#        x = blob.minX() - 10 if blob.minX() > 10 else blob.minX()
#        y = blob.minY() - 10 if blob.minY() > 10 else blob.minY()
#        width = blob.width() + 20 if (blob.width() + 20) < img.width else blob.width() + 10 if( blob.width() + 10 ) < img.width else blob.width()
#        height = blob.height() + 20 if (blob.height() + 20 ) < img.height else blob.height() + 10 if (blob.height() + 10) < img.height else blob.height()
#       return img.crop(x,y,width,height).gaussianBlur().resize(h=50)
        
        new_img = Image(cv2.copyMakeBorder(blob.crop().getNumpyCv2(),20,20,20,20,cv2.BORDER_CONSTANT, value=Color.BLACK), cv2image=True).rotate90()
        return new_img.resize(h=42).invert()
       
    
    def preProcess(self, img):
        return (img - img.binarize().morphOpen()).gaussianBlur().binarize()



    def log(self, plate):
        dt =datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        logging.info("[%s] %s", dt, plate)
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

