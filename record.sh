#!/usr/bin/env bash

FILE=$1
RDIR=records/$FILE

mkdir -p $RDIR

if [ -e $FILE.txt ]; then
    cp $FILE.txt $RDIR/raw.txt
    ./analyze.py < $FILE.txt > $RDIR/analyzed.txt
    ./aggregate.py < $RDIR/analyzed.txt > $RDIR/aggregated.txt

else
    echo "Couldn't find file $FILE.txt"
fi
