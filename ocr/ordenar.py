import string
import os
import shutil

for c in string.ascii_uppercase:
    if not os.path.isdir(c):
        os.mkdir(c)
for d in string.digits:
    if not os.path.isdir(d):
        os.mkdir(d)

for i in os.listdir(os.getcwd()):
    if len(i)<6 or not os.path.isfile(i): continue
    for x in (0,1,2,3,4,5):
        l = i[x].upper()
        print "copiando %s a %s"%(i,os.path.join(l,i))
        shutil.copy(i,os.path.join(l, i))
    shutil.move(i,"copiadas")
