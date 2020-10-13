#!/bin/bash
#

NOW=$(date '+%F %T')

echo "Looking at results for upates within last 10 min at $NOW"
DAY=`date +"%m-%d-%Y"`
NEWEST=$(ls -t results/$DAY/*  -t | head -1)

MIN_BOUNCE=1
MAX_PRICE=5

echo "newest results file: " $NEWEST

python3 bouncer.py $NEWEST $MIN_BOUNCE $MAX_PRICE >> run_logs/look_log.txt

echo "*** Just checked bouncers from file:$NEWEST and at time: `date` *** " >> run_logs/look_log.txt
