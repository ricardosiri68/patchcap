from timeit import default_timer as timer
import ntpath
import sys
import cv2
import os
from platedetector import PlateDetector
import logging 
from stat import *
import multiprocessing
from multiprocessing import Pool, Process, pool
    

def analyze(s, d):
    finder = PlateDetector(False)
    while True:
        f = s.get()
        if f is None: return
        img = cv2.imread(f)
        if img is None:
            logging.error('%s no se pudo abrir',f)
        txt,r = finder.find2(img)
        fn = ntpath.basename(f)
        orig = fn[:6].upper()
        logging.debug("%s: %s"%(fn[:6].upper(),txt))
        d.put((txt, r, txt==orig))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    count = 0
    count_ocr = 0
    st = timer()
    p = '../samples/images/'
    nprocs = multiprocessing.cpu_count() 
    s = multiprocessing.Queue()
    d = multiprocessing.Queue()

    if len(sys.argv)==2:
        p = sys.argv[1]
    mode = os.stat(p)[ST_MODE]
    if S_ISDIR(mode):
        files = [p+f for f in os.listdir(p) if os.path.isfile(p+f)]
    elif S_ISREG(mode):
        files = []
        files.append(p)
    procs = []
    for _ in range(nprocs): 
        p = Process(target=analyze, args=(s, d))
        p.start()
        procs.append(p)
        
    for f in files: s.put(f)
    for _ in range(nprocs): s.put(None)
    for p in procs:
        p.join()

    while not d.empty():
        (txt, img, m) = d.get()         
        if txt and len(txt)>4:
            count_ocr += 1
        if m:
            count = count + 1
    
    logging.debug('se encontraron %s(%s)/%s', count_ocr, count, len(files)) 
    logging.debug('tiempo de exe %s' % (timer()-st))
