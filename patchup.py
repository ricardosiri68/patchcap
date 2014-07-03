#!/usr/bin/env python 
import sys, getopt
from PatchMan.patchman.models import *

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:],"h:a:d:l",["add-plate=",'help','list-all','delete-plate'])
        if not opts:
            raise getopt.GetoptError("Se esperaba un parametro")
        for opt, arg in opts:
            if opt in ('-a','--add-plate'):
                plate = Plate()
                plate.code = arg
                existing = DBSession.query(Plate).filter_by(code=arg).count()
                if not existing:
                    DBSession.add(plate)
                    DBSession.commit()
                else:
                    print "Ya existe esa placa en la base"
            elif opt in ('-d','--delete-plate'):
                DBSession.query(Plate).filter_by(code=arg).delete()
                DBSession.commit()
            elif opt in ('-l','--list-all'):
                plates = DBSession.query(Plate).all()
                for p in plates:
                    print p
    except getopt.GetoptError:
        print usage()
        sys.exit(2)
   

        
def usage():
    msg = sys.argv[0]
    msg += "\n\t[-b | --generate-db] <base.db>\n"
    msg += "\t[-a | --add-plate] <XXXNNN>\n"
    msg += "\t[-d | --delete-plate] <XXXNNN>\n"
    msg += "\t[-l | --list-all] \n"
    print msg


def init_db(dbname='sqlite:///patchcap.db'):
    global engine
    engine = create_engine(dbname, echo=False)
    Session.remove()
    Session.configure(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main(sys.argv)
