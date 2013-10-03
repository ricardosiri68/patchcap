#!/usr/bin/env python
from SimpleCV import ImageSet, Display, Color
from daemon import Daemon
import os, sys, time, datetime, logging
import uuid

class PatchFinder(Daemon):
    def __init__(self,testFolder):
        super(PatchFinder,self).__init__("/tmp/patchfinder.pid", stdin = sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)
        self.images = ImageSet(testFolder)
        logging.info("Iniciando aplicacion")

    def run(self):
        detected = 0

        for img in self.images:
            orig = os.path.splitext(os.path.basename(img.filename))[0].upper()
            logging.debug("procesando %s", orig)
            plate = self.findPlate(img)
            if plate:
                if plate.upper().replace(" ","")[:6] == orig:
                    logging.info ("Detectada OK!")
                    detected+=1
                self.log(plate)
        logging.debug("Detectadas correctamente %d/%d", detected, len(self.images))

    
    def findSimbols(self, img):
        orc = img.readText()
        if orc and not orc.isspace():
            return orc
        return False

    def findPlate(self, img):
        bin = self.preProcess(img)
        
        blobs = list((b for b in bin.findBlobs() if b.isRectangle() and b.area()>1000 and 3 < b.aspectRatio() < 4))
        if not blobs:
            return False

        for b in blobs:
            cropImg = b.crop()

            #el ocr trabaja mejor con caracteres pequenios
            #habria que seguir probando para ver cual es la medida ideal
            if (cropImg.height>42): 
                cropImg=cropImg.resize(h=42)

            #para remover imperfecciones de los bordes
            #habria que ver como mejorar
            cropImg = cropImg.crop(x=3,y=3,w=cropImg.width-6,h=cropImg.height-6)
            plate = self.findSimbols(cropImg)
            if plate:
                return plate


    def preProcess(self, img):
        return (img - img.binarize().morphOpen()).smooth().binarize()


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

