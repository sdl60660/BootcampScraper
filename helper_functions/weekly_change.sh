#LOG TRACKED CHANGES
log_date=$(date "+%Y-%m-%d")
echo "CHANGES OVER THE LAST WEEK: $log_date" >>logs/weekly_change_log.txt
python tracker_results.py 7 ALL>>logs/weekly_change_log.txt
echo "====================================">>logs/weekly_change_log.txt
echo >>logs/weekly_change_log.txt

python generate_plot.py 30 'technologies' 12 False False >> old_data/trend_charts/raw_data/$log_date.plots.txt
python generate_plot.py 30 'locations' 12 False False >> old_data/trend_charts/raw_data/$log_date.plots.txt

python generate_plot.py 30 'technologies' 12 False False 'Selected Camp' >> old_data/trend_charts/raw_data/$log_date.plots.txt
python generate_plot.py 30 'locations' 12 False False 'Selected Camp' >> old_data/trend_charts/raw_data/$log_date.plots.txt


python generate_plot.py 30 'technologies' 12 False False 'Potential Markets' >> old_data/trend_charts/raw_data/$log_date.plots.txt
python generate_plot.py 30 'locations' 12 False False 'Potential Markets' >> old_data/trend_charts/raw_data/$log_date.plots.txt

echo "Tracked Weekly Changes Logged..."