from SimpleCV import ImageSet, Display, Color
import time, os

class PatchFinder:
    def __init__(self,testFolder):
        self.images = ImageSet(testFolder)
#        self.display = Display((800,600))
        self.run()

    
    def drawBlobs(self, img,blobs):
        for b in blobs:
            b.drawRect(color=Color.RED, width=-1,alpha=128)
            img.drawText(str(b.area()),b.x,b.y + 22,Color.BLUE,20)
            img.drawText(str(b.aspectRatio()),b.x,b.y,Color.GREEN,20)

    def validatePlateBlobs(self, blobs):
        for b in blobs:
            cropImg = b.crop()
            if (cropImg.height>45): 
                cropImg=cropImg.resize(h=45)

            if 3 < b.aspectRatio() < 4 and self.findSimbols(cropImg):
                yield b

    def findSimbols(self, img):
        orc = img.readText()
        if orc and not orc.isspace():
            print "ORC",orc
            return True
        else:
            return False

    def findPlate(self, img):
        bin = (img - img.binarize().morphOpen()).smooth(2).binarize()
#        bin = img.grayscale().binarize().morphOpen().smooth()
        img.addDrawingLayer(bin.dl())
        blobs = list((b for b in bin.findBlobs() if b.isRectangle() and b.area>300))
        if blobs:
            filteredBlobs = list(self.validatePlateBlobs(blobs))
            if len(filteredBlobs):
                self.drawBlobs(img, filteredBlobs)


    def run(self):
        for img in self.images:
            print "procesando "+os.path.splitext(os.path.basename(img.filename))[0].upper()
            self.findPlate(img)
            self.saveImage(img)
        
        #self.showImages(5)

    def showImages(self, timeout):
        for img in self.images:
            img.save(self.display)
            time.sleep(timeout)

    def saveImage(self,i):
        poc_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"test")
        name = os.path.basename(i.filename)
        if not os.path.exists(poc_dir):
            os.makedirs(poc_dir)
        i.save(os.path.join(poc_dir, name))

PatchFinder("images/")
