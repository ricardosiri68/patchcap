#!/usr/bin/env python
import sys
import getopt
from patchman.models import Plate, Session, create_engine, Base


def generateDB(arg):
    '''
    genera la base de datos necesaria para correr el programa
    '''
    dbname = 'sqlite:///' + arg
    print "Generando db %s" % (arg)
    init_db(dbname)
    sys.exit()


def addPlate(arg):
    plate = Plate()
    plate.code = arg
    existing = Session.query(Plate).filter_by(code=arg).count()
    if not existing:
        Session.add(plate)
        Session.commit()
    else:
        print "Ya existe esa placa en la base"


def deletePlate(arg):
    Session.query(Plate).filter_by(code=arg).delete()
    Session.commit()


def listPlates():
    plates = Session.query(Plate).all()
    for p in plates:
        print p


def main(argv):
    try:
        opts, args = getopt.getopt(
            argv[1:],
            "b:a:d:l",
            ["generate-db=", "add-plate=", 'list-all', 'delete-plate']
        )
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print usage()
        elif opt in ('-b', '--generate-db'):
            generateDB(arg)
        elif opt in ('-a', '--add-plate'):
            addPlate(arg)
        elif opt in ('-d', '--delete-plate'):
            deletePlate(arg)
        elif opt in ('-l', '--list-all'):
            listPlates()


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
