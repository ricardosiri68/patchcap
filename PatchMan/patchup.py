#!/usr/bin/env python 
import transaction
import sys, getopt
from os import path
from pyramid.paster import bootstrap
from patchman.models import *
from patchman.models import Plate, Device, initialize_sql

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:],
                                "h:a:d:lA:D:L",
                                ['help', "add-device=", "list-devices", "delete-device=", "add-plate=",'list-plates','delete-plate='])
        if not opts:
            raise getopt.GetoptError("Se esperaba un parametro")
        env = bootstrap(path.dirname(path.realpath(__file__))+'/development.ini')
        initialize_sql(env['registry'].settings)
        for opt, arg in opts:
            if opt in ('-a','--add-device'):
                devargs = arg.split(',')
                dev = Device(devargs[0],devargs[1],devargs[2])
                existing = DBSession.query(Device).filter_by(instream=dev.instream).count()
                if not existing:
                    DBSession.add(dev)
                    transaction.commit()
                else:
                    print("Ya existe ese dispositivo en la base")
            elif opt in ('-A','--add-plate'):
                plate = Plate()
                plate.code = arg
                existing = DBSession.query(Plate).filter_by(code=arg).count()
                if not existing:
                    DBSession.add(plate)
                    transaction.commit()
                else:
                    print("Ya existe esa placa en la base")
            elif opt in ('-l','--list-devices'):
                devices = DBSession.query(Device).all()
                for d in devices:
                    print(d)
            elif opt in ('-D','--delete-plate'):
                DBSession.query(Plate).filter_by(code=arg).delete()
            elif opt in ('-L','--list-plates'):
                plates = DBSession.query(Plate).all()
                for p in plates:
                    print(p)
            else:

                print ('Sorry, not implemented')
    except getopt.GetoptError:
        print(usage())
        sys.exit(2)
   

        
def usage():
    msg = sys.argv[0]
    msg += "\n\t[-a | --add-device] <name>,<uri>,<rtsp mount>\n"
    msg += "\t[-d | --delete-device] <uri> \n"
    msg += "\t[-l | --list-devices]\n"
    msg += "\t[-A | --add-plate] <XXXNNN>\n"
    msg += "\t[-D | --delete-plate] <XXXNNN>\n"
    msg += "\t[-L | --list-plates] \n"
    print(msg)


def init_db():
    global engine
    engine = create_engine(dbname, echo=False)
    Session.remove()
    Session.configure(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main(sys.argv)
