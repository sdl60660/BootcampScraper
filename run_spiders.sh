#!/bin/bash

current_time=$(date "+%Y.%m.%d-%H.%M.%S")

echo $current_time >>logs/scraper_log.txt
echo "Scraper started!" >>logs/scraper_log.txt
echo >>logs/scraper_log.txt

#rm bootcampsin_data.json coursereport_data.json switchup_data.json
#echo
#echo "Old JSON files archived..."

rm current_data/*

scrapy crawl bootcampsin -o current_data/bootcampsin_data.json -t json &>logs/command_line_outputs/bootcampsin_logs/$current_time.bootcampsin_output.txt
echo
echo "BootcampsIn Spider Finished..."    

scrapy crawl switchup -o current_data/switchup_data.json -t json &>logs/command_line_outputs/switchup_logs/$current_time.switchup_output.txt
echo
echo "SwitchUp Spider Finished..." 

scrapy crawl coursereport -o current_data/coursereport_data.json -t json &>logs/command_line_outputs/coursereport_logs/$current_time.coursereport_output.txt 
echo
echo "CourseReport Spider Finished..."

python cr_clean.py current_data/coursereport_data.json
rm current_data/coursereport_data.json
mv clean_coursereport_data.json current_data/coursereport_data.json

echo

python json_merge.py current_data/bootcampsin_data.json current_data/switchup_data.json current_data/coursereport_data.json
echo "Merge Finished..."

#mv bootcampsin_data.json current_data
#mv switchup_data.json current_data
#mv coursereport_data.json current_data

cp current_data/bootcampsin_data.json old_data/bootcampsin/bootcampsin_data.$current_time.json
cp current_data/switchup_data.json old_data/switchup/switchup_data.$current_time.json
cp current_data/coursereport_data.json old_data/coursereport/coursereport_data.$current_time.json

echo "Files Moved..."
echo "Old JSON files archived..."

mv output.json current_data
cp current_data/output.json old_data/full_outputs/output.$current_time.json


#ADD SOMETHING HERE THAT RUNS THE SEARCH FUNCTION WITH A BLANK OUTPUT
#IN SEARCH FUNCTION, ADD OPTION SO THAT BLANK INPUT OUTPUTS JUST A SET OF
#STATS, NOT ANY BOOTCAMP STATS IN PARTICULAR

#ADD THIS RESULT TO THE SCRAPER_LOG
#KEEP STATS VERY BASIC (i.e. number of bootcamps in output.json), IT'S A
#LOG, NOT WHAT YOU'LL USE TO TRACK CHANGES

current_time=$(date "+%Y.%m.%d-%H.%M.%S")
echo $current_time >>logs/scraper_log.txt
echo "Scraper finished!" >>logs/scraper_log.txt

echo
echo "Done!"
echo


