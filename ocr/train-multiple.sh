#!/bin/bash
if test $# -ne 3;then
    echo 'ERROR: no se especifico el nro de exp'
    exit 1
fi

tesseract spa.patentes.exp$1.tif spa.patentes.exp$1 nobatch box.train
tesseract spa.patentes.exp$2.tif spa.patentes.exp$2 nobatch box.train
tesseract spa.patentes.exp$3.tif spa.patentes.exp$3 nobatch box.train
unicharset_extractor spa.patentes.exp$1.box spa.patentes.exp$2.box spa.patentes.exp$3.box

echo "patentes 0 1 1 0 0" > spa.font_properties
shapeclustering -F spa.font_properties -U unicharset spa.patentes.exp$1.tr spa.patentes.exp$2.tr spa.patentes.exp$3.tr

mftraining -F spa.font_properties -U unicharset -O spa.unicharset spa.patentes.exp$1.tr spa.patentes.exp$2.tr spa.patentes.exp$3.tr
cntraining spa.patentes.exp$1.tr spa.patentes.exp$2.tr spa.patentes.exp$3.tr
mv shapetable spa.shapetable
mv inttemp spa.inttemp
mv normproto spa.normproto
mv pffmtable spa.pffmtable
wordlist2dawg words_list spa.word-dawg spa.unicharset
combine_tessdata spa.
rm spa.font_properties spa.unicharset spa.inttemp spa.word-dawg spa.pffmtable spa.normproto spa.patentes.exp$1.tr spa.patentes.exp$2.tr spa.patentes.exp$3.txt unicharset
