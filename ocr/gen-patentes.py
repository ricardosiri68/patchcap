import string
with open("patentes.txt", "a") as f:
    for a in string.ascii_uppercase:
        for b in string.ascii_uppercase:
            for c in string.ascii_uppercase:
                for n in range(0,9):
                    for m in range(0,9):
                        for i in range(0,9):
                            f.write("%s%s%s %s%s%s\n"%(a,b,c,n,m,i))
f.close()





