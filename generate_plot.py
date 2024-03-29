import sys
sys.path.insert(0, '~/scrapy_projects/bootcamp_info')

import tracking
from tracking import tracking_groups

from tracking import plot_changes
from utilities import return_closest

import datetime
from datetime import date

def main():
	if len(sys.argv) < 5:
		print 'USAGE: python generate_plot.py [days_back] [category] [max_items] [percentage_option] [show_plot] (OPTIONAL:) [tracking_group]'
		sys.exit()

	days_back = int(sys.argv[1])
	category = sys.argv[2]
	max_items = int(sys.argv[3])

	if sys.argv[4].title() == 'True':
		percentage = True
	else:
		percentage = False

	if sys.argv[5].title() == 'True':
		show = True
	else:
		show = False

	if len(sys.argv) > 6:
		tgroup = sys.argv[6]
	else:
		tgroup = None

	today = date.today()
	db_date = date.fromordinal(today.toordinal() - days_back)

	print_string = 'Plot information for ' + str(category).title() + ' (Dates: ' + str(db_date) + ' to ' + str(today) + ', Max Items: ' + str(max_items) + ')'
	if tgroup:
		print_string = print_string[:-1] + ', Tracking Group: ' + str(tgroup).title() + ')'
	print print_string
	print '-------------------------------------------------------'
	print
	
	plot_changes(days_back, category, max_items=max_items, start_item=0, percentage=percentage, interval=1,
	 active_only=True, tracking_group=tgroup, show_plot=show, save_plot=True, current_status=False)

	print
if __name__ == '__main__':
  main()


#1. DONE! GET PLOT FOR NUMBER OF CAMPS IN META TRACKING CATEGORIES (OVERALL IN 'POTENTIAL MARKETS' AND EACH POTENTIAL MARKET, FOR EXAMPLE)
#2. DONE! SETUP OPTION FOR PLOTS TO SAVE TO CERTAIN FOLDER IN OLD_DATA
#2b. OPTION TO EXPORT RAW PLOT DATA TO A LOG FILE
#3. BUILD OUT OTHER PLOT FUNCTIONS
#4. DECIDE WHAT WOULD BE HELPFUL TO PLOT EVERY MONTH (MAYBE EVERY WEEK)
#5. WRITE A BASH SCRIPT TO RUN THE APPROPRIATE PLOTS FROM GENERATE_PLOT.PY FOR ABOVE
#6. ADD A MONTHLY OR WEEKLY CRONJOB TO RUN THIS SCRIPT AND STORE PLOTS IN AN OLD_DATA FOLDER OR SEPARATE DATA FOLDER