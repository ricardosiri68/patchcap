#!/usr/bin/env python
from SimpleCV import ImageSet, Display, Color
from daemon import Daemon
import os, sys, time, datetime, logging
import uuid

class PatchFinder(Daemon):
    def __init__(self,testFolder):
        super(PatchFinder,self).__init__(
                "/tmp/patchfinder.pid", stdin = sys.stdin,
                stdout=sys.stdout, stderr=sys.stderr
                )
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)
        self.images = ImageSet(testFolder)
        logging.info("Iniciando aplicacion")

    def run(self):
        detected = 0

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

    def cropInnerChar(self,blob, img):
        '''
        corta los blobs que se encuentran dentro del crop de la patente
        con un padding de 3px o menos
        '''
        x = blob.minX() - 3 if blob.minX() > 3 else blob.minX()
        y = blob.minY() - 3 if blob.minY() > 3 else blob.minY()
        width = blob.width() + 6 if (blob.width() + blob.minX() + 6) < img.width else blob.width() + 3 if( blob.minX() + blob.width() + 3 ) < img.width else blob.width()
        height = blob.height() + 6 if (blob.height() + blob.minY() + 6 ) < img.height else blob.height() + 3 if (blob.minY() + blob.height() + 3) < img.height else blob.height()
        return img.crop(x,y,width,height)

    def findInnerChars(self,img):
        '''
        busca 6 o mas blobs dentro de la patente y evalua sus caracteres uno por uno
        los genera y luego findSimbols los lista y los agrupa en un string
        '''
        blobs = img.invert().findBlobs()

        if blobs and len(blobs) >= 6:
            if not os.path.isdir("blobsChars/%s" % id(img)):
                os.mkdir("blobsChars/%s" % id(img))
            for b in blobs:
                croped = self.cropInnerChar(b,img)
                croped.save("blobsChars/%s/%s.jpg" % (id(img),id(croped)) )
                char = croped.readText()
                if char:
                   yield  char

    def findSimbols(self, img):
        orc = "".join(list(self.findInnerChars(img.copy())))
        # orc = img.readText()
        if orc:
            print orc
            return orc.strip()
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
            #cropImg = cropImg.crop(x=3,y=3,w=cropImg.width-6,h=cropImg.height-6)
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

