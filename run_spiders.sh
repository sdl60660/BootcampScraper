#!/bin/bash

echo
current_time=$(date "+%H:%M:%S")
echo "$current_time: Scraper started!"

current_time=$(date "+%Y.%m.%d-%H:%M:%S")
echo $current_time >>logs/scraper_log.txt
echo "Scraper started!" >>logs/scraper_log.txt
echo >>logs/scraper_log.txt

#mkdir old_data/switchup/temp_switchup_files
rm old_data/switchup/temp_switchup_files/*
mv current_data/switchup_data.json old_data/switchup/temp_switchup_files/switchup_data.json
rm current_data/*

#BOOTCAMPSIN SPIDER
scrapy crawl bootcampsin -o current_data/bootcampsin_data.json -t json &>logs/command_line_outputs/bootcampsin_logs/$current_time.bootcampsin_output.txt
echo
output_time=$(date "+%H:%M:%S")
echo "$output_time: BootcampsIn Spider Finished..."

#SWITCHUP SPIDER

switchup_array=()
for i in `seq 1 5`;
do
	index=($i - 1)
	switchup_array[$index]="old_data/switchup/temp_switchup_files/switchup_data$i.json"
	scrapy crawl switchup -o old_data/switchup/temp_switchup_files/switchup_data$i.json -t json &>logs/command_line_outputs/switchup_logs/$current_time.switchup_output$i.txt
done

echo $switchup_array

rm old_data/switchup/temp_switchup_files/merged_switchup_data.json
touch old_data/switchup/temp_switchup_files/merged_switchup_data.json
python json_merge.py "${switchup_array[@]}" --output old_data/switchup/temp_switchup_files/merged_switchup_data.json
#merge today's full switchup JSON with yesterday's. This way if only 265/272 are caught, the rest can be filled in with
#old values. Over time, this should keep everything that's not up-to-date as of today at least only a day or two old.
touch current_data/switchup_data.json
python json_merge.py old_data/switchup/temp_switchup_files/merged_switchup_data.json old_data/switchup/temp_switchup_files/switchup_data.json --output current_data/switchup_data.json

output_time=$(date "+%H:%M:%S")
echo "$output_time: SwitchUp Spider Finished..."


#COURSEREPORT SPIDER
scrapy crawl coursereport -o current_data/coursereport_data.json -t json &>logs/command_line_outputs/coursereport_logs/$current_time.coursereport_output.txt 
output_time=$(date "+%H:%M:%S")
echo "$output_time: CourseReport Spider Finished..."

python cr_clean.py current_data/coursereport_data.json
rm current_data/coursereport_data.json
mv clean_coursereport_data.json current_data/coursereport_data.json

echo

#MERGE JSONS
python json_merge.py current_data/bootcampsin_data.json current_data/switchup_data.json current_data/coursereport_data.json
output_time=$(date "+%H:%M:%S")
echo "$output_time: Merge Finished..."

#ARCHIVE CURRENT DATA
cp current_data/bootcampsin_data.json old_data/bootcampsin/$current_time.bootcampsin_data.json
cp current_data/switchup_data.json old_data/switchup/$current_time.switchup_data.json
cp current_data/coursereport_data.json old_data/coursereport/$current_time.coursereport_data.json

output_time=$(date "+%H:%M:%S")
echo "$output_time: Files Archived..."

#ARCHIVE FULL OUTPUT
mv output.json current_data
cp current_data/output.json old_data/full_outputs/$current_time.output.json


#ADD SOMETHING HERE THAT RUNS THE SEARCH FUNCTION WITH A BLANK OUTPUT
#IN SEARCH FUNCTION, ADD OPTION SO THAT BLANK INPUT OUTPUTS JUST A SET OF
#STATS, NOT ANY BOOTCAMP STATS IN PARTICULAR

#ADD THIS RESULT TO THE SCRAPER_LOG
#KEEP STATS VERY BASIC (i.e. number of bootcamps in output.json), IT'S A
#LOG, NOT WHAT YOU'LL USE TO TRACK CHANGES

output_time=$(date "+%H:%M:%S")
echo
echo "$output_time: Scraper finished!"

current_time=$(date "+%Y.%m.%d-%H:%M:%S")
echo $current_time >>logs/scraper_log.txt
echo "Scraper finished!" >>logs/scraper_log.txt
echo "-------------------" >>logs/scraper_log.txt
echo >>logs/scraper_log.txt

echo
echo "Done!"
echo


