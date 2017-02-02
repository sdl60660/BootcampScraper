#!/bin/bash

cd ~/scrapy_projects/bootcamp_info

#IN CASE NOT ALREADY ACTIVATED
source ~/.virtualenvs/scrapy_venv/bin/activate

export PYTHONPATH="${PYTHONPATH}:~/scrapy_projects/bootcamp_info"
export SLACK_BOT_TOKEN='xoxb-84508800582-zdQenvCLGRrmF1v4rafaUEQb'
export BOT_ID='U2GEYPJH4'

echo
current_time=$(date "+%H:%M:%S")
echo "$current_time: Scraper started!"

current_time=$(date "+%Y-%m-%d.(%H:%M:%S)")
echo $current_time >>logs/scraper_log.txt
echo "Scraper started!" >>logs/scraper_log.txt
echo >>logs/scraper_log.txt

#mkdir old_data/switchup/temp_switchup_files
rm old_data/switchup/temp_switchup_files/*
mv current_data/switchup_data.json old_data/switchup/temp_switchup_files/switchup_data.json
rm current_data/coursereport_data.json current_data/output.json

#BOOTCAMPSIN SPIDER
#scrapy crawl bootcampsin -o current_data/bootcampsin_data.json -t json &>logs/command_line_outputs/bootcampsin_logs/$current_time.bootcampsin_output.txt
#echo
#output_time=$(date "+%H:%M:%S")
#echo "$output_time: BootcampsIn Spider Finished..."

#SWITCHUP SPIDER

switchup_array=()
for i in `seq 1 2`;
do
	index=($i - 1)
	switchup_array[$index]="old_data/switchup/temp_switchup_files/switchup_data$i.json"
	scrapy crawl switchup -o old_data/switchup/temp_switchup_files/switchup_data$i.json -t json &>logs/command_line_outputs/switchup_logs/$current_time.switchup_output$i.txt
done

echo $switchup_array

#rm old_data/switchup/temp_switchup_files/merged_switchup_data.json
touch old_data/switchup/temp_switchup_files/merged_switchup_data.json
python helper_functions/json_merge.py "${switchup_array[@]}" --output old_data/switchup/temp_switchup_files/merged_switchup_data.json
#merge today's full switchup JSON with yesterday's. This way if only 265/272 are caught, the rest can be filled in with
#old values. Over time, this should keep everything that's not up-to-date as of today at least only a day or two old.
python helper_functions/json_merge.py old_data/switchup/temp_switchup_files/switchup_data.json old_data/switchup/temp_switchup_files/merged_switchup_data.json --output current_data/switchup_data.json

#If anything in this process fails for any reason and there is no switchup_data file left in current_data, we need to move
#the old one back so that the full script is repeatable without having to move around swtichup_data files
if [ -s current_data/switchup_data.json ]
then
	:
else
	mv old_data/switchup/temp_switchup_files/switchup_data.json current_data/switchup_data.json
	echo >>logs/scraper_log.txt
	echo "WARNING: THERE WAS AN ERROR WITH THE SWITCHUP DATA MERGE, MOVING OLD SWITCHUP FILE BACK TO 'CURRENT_DATA'" >>logs/scraper_log.txt
	echo
	echo "WARNING: THERE WAS AN ERROR WITH THE SWITCHUP DATA MERGE, MOVING OLD SWITCHUP FILE BACK TO 'CURRENT_DATA'"
fi


output_time=$(date "+%H:%M:%S")
echo "$output_time: SwitchUp Spider Finished..."


#COURSEREPORT SPIDER
scrapy crawl coursereport -o current_data/coursereport_data.json -t json &>logs/command_line_outputs/coursereport_logs/$current_time.coursereport_output.txt 
output_time=$(date "+%H:%M:%S")
echo "$output_time: CourseReport Spider Finished..."

python helper_functions/cr_clean.py current_data/coursereport_data.json
rm current_data/coursereport_data.json
mv clean_coursereport_data.json current_data/coursereport_data.json

echo

#MERGE JSONS
python helper_functions/techlist_pipeline_fix.py current_data/coursereport_data.json temp_output.json
mv temp_output.json current_data/coursereport_data.json

python helper_functions/techlist_pipeline_fix.py current_data/switchup_data.json temp_output.json
mv temp_output.json current_data/switchup_data.json

#python helper_functions/json_merge.py current_data/bootcampsin_data.json current_data/switchup_data.json current_data/coursereport_data.json
python helper_functions/json_merge.py current_data/switchup_data.json current_data/coursereport_data.json
output_time=$(date "+%H:%M:%S")
echo "$output_time: Merge Finished..."

#ARCHIVE CURRENT DATA
#cp current_data/bootcampsin_data.json old_data/bootcampsin/$current_time.bootcampsin_data.json
cp current_data/switchup_data.json old_data/switchup/$current_time.switchup_data.json
cp current_data/coursereport_data.json old_data/coursereport/$current_time.coursereport_data.json

output_time=$(date "+%H:%M:%S")
echo "$output_time: Files Archived..."

#ARCHIVE FULL OUTPUT
mv output.json current_data
cp current_data/output.json old_data/full_outputs/$current_time.output.json

#PULL OUT TRACKING GROUP INFO
rm current_data/tracking_groups/*
python helper_functions/tgroup_sort.py current_data/output.json

#ADD META DATA TO TRACKING GROUP FILES
python helper_functions/json_merge.py current_data/tracking_groups/current_markets.json current_data/tracking_groups/current_markets.json --output current_data/tracking_groups/current_markets.json >/dev/null
python helper_functions/json_merge.py current_data/tracking_groups/java_and_NET.json current_data/tracking_groups/java_and_NET.json --output current_data/tracking_groups/java_and_NET.json >/dev/null
python helper_functions/json_merge.py current_data/tracking_groups/potential_markets.json current_data/tracking_groups/potential_markets.json --output current_data/tracking_groups/potential_markets.json >/dev/null
python helper_functions/json_merge.py current_data/tracking_groups/top_camps.json current_data/tracking_groups/top_camps.json --output current_data/tracking_groups/top_camps.json >/dev/null
python helper_functions/json_merge.py current_data/tracking_groups/selected_camps.json current_data/tracking_groups/selected_camps.json --output current_data/tracking_groups/selected_camps.json >/dev/null

#ARCHIVE TRACKING GROUP DATA
cp current_data/tracking_groups/current_markets.json old_data/tracking_groups/current_markets/$current_time.current_markets.json
cp current_data/tracking_groups/potential_markets.json old_data/tracking_groups/potential_markets/$current_time.potential_markets.json
cp current_data/tracking_groups/top_camps.json old_data/tracking_groups/top_camps/$current_time.top_camps.json
cp current_data/tracking_groups/java_and_NET.json old_data/tracking_groups/Java_and_.NET/$current_time.java_and_NET.json
cp current_data/tracking_groups/selected_camps.json old_data/tracking_groups/selected_camps/$current_time.selected_camps.json

output_time=$(date "+%H:%M:%S")
echo "$output_time: Tracking Group Data Files Sorted..."

#LOG SEARCH TERMS
rm current_data/search_terms.csv
python helper_functions/search_terms.py

echo 'META DATA FROM LAST OUTPUT' >>logs/scraper_log.txt
echo '--------------------------' >>logs/scraper_log.txt
echo >>logs/scraper_log.txt
python bootcamp_search.py 'meta' >>logs/scraper_log.txt
echo >>logs/scraper_log.txt

echo 'WARNING: These possible duplicates were found:' >>logs/scraper_log.txt
python helper_functions/possible_duplicate_search.py current_data/output.json >>logs/scraper_log.txt
echo >>logs/scraper_log.txt

#LOG TRACKED CHANGES
log_date=$(date "+%Y-%m-%d")
echo "CHANGES FOR $log_date" >>logs/change_log.txt
python trend_functions/tracker_results.py 1 ALL>>logs/change_log.txt
echo "====================================">>logs/change_log.txt
echo >>logs/change_log.txt
output_time=$(date "+%H:%M:%S")
echo "$output_time: Tracked Changes Logged..."

current_time=$(date "+%Y-%m-%d.(%H:%M:%S)")
echo $current_time >>logs/scraper_log.txt
echo "Scraper finished!" >>logs/scraper_log.txt
echo "-------------------" >>logs/scraper_log.txt
echo >>logs/scraper_log.txt

python helper_functions/tgroup_dict.py
python slackbot/post_changes.py

#location_changes="$(python helper_functions/location_track_wrapper.py)"
#osascript -e "display notification '$location_changes' with title 'Location Changes'"

output_time=$(date "+%H:%M:%S")
echo
echo "$output_time: Scraper finished!"

osascript -e 'display notification "Bootcamp scraper has finished!" with title "Bootcamp Scraper"'

