#!/bin/bash
#

NOW=$(date '+%F %T')

echo "Looking at results for upates within last 5 min at $NOW"
DAY=`date +"%m-%d-%Y"`
NEWEST=$(ls -t results/$DAY/*  -t | head -1)

MIN_BOUNCE=0
MAX_PRICE=0.3

echo "newest results file: " $NEWEST

python3 bouncer.py $NEWEST $MIN_BOUNCE $MAX_PRICE >> run_logs/look_log.txt

echo "*** Just checked bouncers from file:$NEWEST and at time: `date` *** " >> run_logs/look_log.txt
