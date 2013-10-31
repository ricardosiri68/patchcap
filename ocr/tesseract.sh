#!/bin/bash
plate=
dir=$PWD

if [ $# > 1 ];then
    dir=$1
fi
cd $dir
rm -f *.txt

pate=`basename $dir`
i=0
echo "analizando $pate"
for ((i=0; i<6; i++)); do      
    c=`echo ${pate:$i:1}`
    if [ $i -ge 7 ]; then
        conf="digits"
    else
        conf=
    fi
    tesseract -psm 10 $c.png $c $conf 1>/dev/null
    plate="$plate`cat "$c.txt"`"
done
echo $plate

cd $OLDPWD

