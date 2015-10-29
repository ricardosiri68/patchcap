#!/usr/bin/env python 
import transaction
import sys, getopt
from os import path
from pyramid.paster import bootstrap
import client
import json

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:],
                                "h:a:d:lA:D:L",
                                ['help', "add-device=", "list-devices", "delete-device=", "add-plate=",'list-plates','delete-plate='])
        if not opts:
            raise getopt.GetoptError("Se esperaba un parametro")

        backend = client.Backend()

        for opt, arg in opts:
            if opt in ('-a','--add-device'):
                devargs = arg.split(',')
                dev = {'name': devargs[0], 'instream': devargs[1], 'outstream': devargs[2]}
                r = backend.add_device(dev)
                if r.status_code !=201:
                    print ("Error", r.text)

            elif opt in ('-l','--list-devices'):
                r = backend.devices()
		if r.error():
			print r.result
		else:
                	for d in r.result:
                    		print(json.dumps(d, sort_keys=True, indent=4, separators=(',',': ' )))
            elif opt in ('-d','--delete-device'):
                backend.delete_device(arg)

            elif opt in ('-A','--add-plate'):
                plate = Plate()
                plate.code = arg
                existing = DBSession.query(Plate).filter_by(code=arg).count()
                if not existing:
                    DBSession.add(plate)
                    transaction.commit()
                else:
                    print("Ya existe esa placa en la base")

            elif opt in ('-d','--delete-plate'):
                dbsession.query(plate).filter_by(code=arg).delete()

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
    msg += "\t[-d | --delete-device] id \n"
    msg += "\t[-l | --list-devices]\n"
    msg += "\t[-A | --add-plate] <XXXNNN>\n"
    msg += "\t[-D | --delete-plate] <XXXNNN>\n"
    msg += "\t[-L | --list-plates] \n"
    print(msg)


if __name__ == "__main__":
    main(sys.argv)
