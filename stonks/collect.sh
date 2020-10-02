#!/bin/bash
#


echo Ending old ongoing scrape programs..
pkill -f scrap.py

DAY=`date +"%m-%d-%Y"`
NOW=`date +"%m-%d-%Y-%T"`
FILENAME="results/$DAY/${NOW}_nmout.txt"


mkdir -p "results/$DAY"

echo "Fetching current options info at $NOW and adding to file: $FILENAME"

python3 scrap.py >> $FILENAME &

printf "Finished running scrap on cron..\n\n"

