#!/bin/bash
#

echo "Looking at results from last X min.."
DAY=`date +"%m-%d-%Y"`
NEWEST=$(ls -t results/$DAY/*  -t | head -2 | tail -1)

echo "newest results file: " $NEWEST


python3 bouncer.py $NEWEST >> run_logs/look_log.txt
