#!/bin/sh
#################################################################
# Usage:
#
# sh preprocessor.sh /in myPlainCorpus
#################################################################

#TODO für in verzeichnis
#echo "Create unique ..."
#sort -u -k2  $RES/$1.sentences  -o $RES/$1.sentences
echo "Start Pre-Preprocessing"
python3.3 python/pipeline.py $1 $2 $3

