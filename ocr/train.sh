#!/bin/bash
tesseract spa.patentes.exp3.tiff spa.patentes.exp3.box nobatch box.train
unicharset_extractor spa.patentes.exp3.box
echo "patentes 0 1 1 0 0" > spa.font_properties
mftraining -F spa.font_properties -U unicharset -O spa.unicharset spa.patentes.exp3.box.tr
cntraining spa.patentes.exp3.box.tr
mv Microfeat spa.Microfeat
mv inttemp spa.inttemp
mv normproto spa.normproto
mv pffmtable spa.pffmtable
wordlist2dawg words_list spa.word-dawg spa.unicharset
combine_tessdata spa.
rm spa.font_properties spa.Microfeat spa.unicharset spa.inttemp spa.word-dawg spa.pffmtable spa.normproto spa.patentes.exp3.box.tr spa.patentes.exp3.box.txt unicharset
