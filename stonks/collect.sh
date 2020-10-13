#!/bin/bash
#


echo Ending old ongoing scrape programs..
pkill -f fetcher.py

DAY=`date +"%m-%d-%Y"`
NOW=`date +"%m-%d-%Y-%T"`
FILENAME="results/$DAY/${NOW}_nmout.txt"

STOCK_TARGS="LUV--SAVE--AEO"

mkdir -p "results/$DAY"

echo "Fetching current options info from tws at $NOW and adding to file: $FILENAME"

python3 fetcher.py $STOCK_TARGS >> $FILENAME &

printf "Finished running tws price fetcher on cron..\n\n"

