#!/bin/bash
if test $# -ne 1;then
    echo 'ERROR: no se especifico el nro de exp'
    exit 1
fi
tesseract spa.patentes.exp$1.tif spa.patentes.exp$1 nobatch box.train
unicharset_extractor spa.patentes.exp$1.box
echo "patentes 0 1 1 0 0" > spa.font_properties
#shapeclustering -F spa.font_properties -U unicharset spa.patentes.exp$1.tr
mftraining -F spa.font_properties -U unicharset -O spa.unicharset spa.patentes.exp$1.tr
cntraining spa.patentes.exp$1.tr
mv shapetable spa.shapetable
mv inttemp spa.inttemp
mv normproto spa.normproto
mv pffmtable spa.pffmtable
wordlist2dawg words_list spa.word-dawg spa.unicharset
combine_tessdata spa.
rm spa.font_properties spa.unicharset spa.inttemp spa.word-dawg spa.pffmtable spa.normproto spa.patentes.exp$1.tr spa.patentes.exp$1.txt unicharset
