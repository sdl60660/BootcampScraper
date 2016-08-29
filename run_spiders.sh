#!/bin/bash

rm test_bootcampsin.json test_coursereport.json test_switchup.json
echo
echo "Old JSON files archived..."

scrapy crawl bootcampsin -o test_bootcampsin.json -t json # &>command_line_outputs/bootcampsin_output.txt
echo
echo "BootcampsIn Spider Finished..."    

scrapy crawl switchup -o test_switchup.json -t json #  &>command_line_outputs/switchup_output.txt
echo
echo "SwitchUp Spider Finished..." 

scrapy crawl coursereport -o test_coursereport.json -t json #  &>command_line_outputs/coursereport_output.txt 
echo
echo "CourseReport Spider Finished..."

echo


rm output.json
python json_merge.py test_bootcampsin.json test_switchup.json test_coursereport.json
echo "Merge Finished"


echo
echo "Done!"
echo


