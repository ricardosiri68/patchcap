#!/usr/bin/env python
import log, sys, time, datetime
import logging, logging.config
import cv2.cv as cv
import transaction
from cv2 import copyMakeBorder, BORDER_CONSTANT 
from SimpleCV import Color, Image, Camera,JpegStreamer, JpegStreamCamera, VirtualCamera
from daemon import Daemon
from os import path, mkdir, listdir
from ocr import Ocr
from pyramid.paster import bootstrap
from patchman.models import * 
from device import VirtualDevice

logger = log.setup()


class PatchFinder(Daemon):

    def __init__(self,src):
        self.env = None

        super(PatchFinder,self).__init__("/tmp/patchfinder.pid",stdin='/dev/stdin', stderr='/dev/stderr',stdout='/dev/stdout')

        self.device = VirtualDevice(src)

    def run(self):
        
        logger.info("Iniciando aplicacion")
        self.env = bootstrap('PatchMan/development.ini')
        self.ocr = Ocr('spa')
        initialize_sql(self.env['registry'].settings)
        self.js = JpegStreamer()
        detected = 0
        total = 0
        print dir(self.env)
        while True:
            img = self.device.getImage()
            if img is False: 
                break
            elif not img:
                continue
            detected+=self.comparePlate(img)
            total +=1
            #time.sleep(1)
            img.save(self.js) 
        logger.info("Detectadas correctamente %d/%d", detected, total)
        
    def comparePlate(self, img):
        if img.filename:
            real = path.splitext(path.basename(img.filename))[0].upper()
        else:
            real = None
        plate = self.findPlate(img)
        if plate:
            #self.log(plate)
            if real:
                output = plate.upper().replace(" ","")[:6]
                if output == real[:6]:
                    logger.debug("\033[92m"+output+": OK \033[0m")
                    return 1
                else:
                    logger.debug(real[:6]+": "+output)
                    return 0
            else:
                return self.isPlate(plate)
        return 0


    def isPlate(self, plate):
        return len(plate)==6 and \
                len(filter(lambda x: x in '1234567890', list(plate)))==3

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

        img_name = path.splitext(path.basename(imgname))[0].upper()
        
        if logger.isEnabledFor(logging.DEBUG):
            if not path.isdir("blobsChars/%s" % img_name):
                mkdir("blobsChars/%s" % img_name)
            imgpath = "blobsChars/%s/%s.jpg"%(img_name,img_name)
            img = img.crop(3,3,img.width-6,img.height-6).resize(h=50)
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

    def preProcess(self, img):
        return (img - img.binarize().morphOpen()).gaussianBlur().binarize()


    def log(self, plate):
        dt =datetime.now().strftime("%Y-%m-%d %H:%M")
        transaction.begin()
        p= DBSession.query(Plate).filter_by(code=plate).first()
        if p is None:
            p=Plate(plate, active=False, notes="Agregada automaticamente...")
            DBSession.add(p)

        log = PlateLog()
        log.plate = p
        DBSession.add(log)
        transaction.commit()

    def __del__(self):
        self.device = None
        if self.env:
            self.env['closer']()
            del self.env

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

