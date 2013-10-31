import string
with open("words_list.txt", "w") as f:
    for a in string.ascii_uppercase:
        for b in string.ascii_uppercase:
            c = 'A'
        #            for c in string.ascii_uppercase:
            f.write("%s%s%s "%(a,b,c))
        f.write("\n")
        #f.write("\n")

    for n in range(0,10):
        for m in range(0,10):
        #            for i in range(0,10):
            i = '8'
            f.write("%s%s%s "%(n,m,i))
            #f.write("\n")
    f.write("\n")
f.close()





