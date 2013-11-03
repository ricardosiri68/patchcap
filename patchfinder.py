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

    logEnabled = True
    
    def __init__(self,src, logEnabled = True):
        self.env = None
        super(PatchFinder,self).__init__("/tmp/patchfinder.pid",stdin='/dev/stdin', stderr='/dev/stderr',stdout='/dev/stdout')
        self.device = VirtualDevice(src)
        self.logEnabled = str(logEnabled) in ('True','1')
        
        if self.logEnabled:
            logger.debug("Se escribiran los logs a la base")
        
    def run(self):
        if self.logEnabled:
            self.env = bootstrap('PatchMan/development.ini')
            initialize_sql(self.env['registry'].settings)
        
        stats = PatchStat()
        output = OutputStream()
        finder = PlateFinder(stats)
        

        while True:
            img = self.device.getImage()
            if not img:
                break;
            stats.count()
            plate = finder.find(img)
            if plate:
                self.log(img, plate, stats)
            output.write(img, plate)

        stats.show()

    def log(self, img, plate, stats):

        if self.logEnabled:
            logger.debug("loging capture to db")
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
       
        if img.filename:
            real = path.splitext(path.basename(img.filename))[0].upper()
            output = plate.upper().replace(" ","")[:6]
            if output == real[:6]:
                logger.debug("\033[92m"+output+": OK \033[0m")
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

