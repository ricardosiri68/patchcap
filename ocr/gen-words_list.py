import string
with open("words_list", "a") as f:
    for a in string.ascii_uppercase:
        for b in string.ascii_uppercase:
            for c in string.ascii_uppercase:
                f.write("%s%s%s\n"%(a,b,c))
    for n in range(0,10):
        for m in range(0,10):
            for i in range(0,10):
                f.write("%s%s%s\n"%(n,m,i))
f.close()





