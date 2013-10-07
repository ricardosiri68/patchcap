#!/bin/bash
plate=
for d in {0..5}; do
    if [[ "$d" > "2.jpg" ]]; then
        conf="digits"
    else
        conf=
    fi
    tesseract -psm 10 $d.jpg $d $conf 1>/dev/null
    plate="$plate`cat "$d.txt"`"
done
echo $plate
