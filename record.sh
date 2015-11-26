#!/usr/bin/env bash

FILE=$1
RDIR=records/$FILE

mkdir $RDIR

cp $FILE.txt $RDIR/raw.txt
./analyze.py < $FILE.txt > $RDIR/analyzed.txt
./aggregate.py < $RDIR/analyzed.txt > $RDIR/aggregated.txt
