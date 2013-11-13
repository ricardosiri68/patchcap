#!/usr/bin/env python
import log, sys, datetime
from os import path
import logging, logging.config
import transaction
from SimpleCV import Image
from daemon import Daemon
from pyramid.paster import bootstrap
from patchman.models import * 
from device import VirtualDevice
from platefinder import PlateFinder
from outputstream import OutputStream
from stats import PatchStat

logger = log.setup()

class PatchFinder(Daemon):

    capEnabled = True
    
    def __init__(self,src, logEnabled = 'True'):
        self.env = None
        super(PatchFinder,self).__init__("/tmp/patchfinder.pid",stdin='/dev/stdin', stderr='/dev/stderr',stdout='/dev/stdout')
        self.device = VirtualDevice(src)
        self.capEnabled = str(logEnabled) in ('True','1')
        
        if self.capEnabled:
            logger.debug("Se escribiran los logs a la base")
        
    def run(self):
        if self.capEnabled:
            self.env = bootstrap('PatchMan/development.ini')
            initialize_sql(self.env['registry'].settings)
        
        stats = PatchStat()
        output = OutputStream()
        finder = PlateFinder()

        while True:
            img = self.device.getImage()
            if not img:
                stats.error()
                break;
            stats.count()
            code = finder.find(img)
            if Plate.isPlate(code):
                if self.capEnabled:
                    logger.debug("loging capture to db")
                    transaction.begin()
                    plate = Plate.findBy(code)
                    if plate.active:
                        self.device.alarm()
                    plate.log()
                    transaction.commit()
                self.log(img, code, stats)
            else:
                code = ''
            output.write(img, code)

        stats.show()

    
    def log(self, img, plate, stats):
        stats.detected()
        if img.filename:
            real = path.splitext(path.basename(img.filename))[0].upper()
            output = plate.upper().replace(" ","")[:6]
            if output == real[:6]:
                logger.debug("\033[92m"+output+": OK \033[0m")
                stats.found()
            else:
                logger.debug(real[:6]+": "+output)
            
    
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
