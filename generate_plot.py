import tracking
from tracking import tracking_groups

from tracking import plot_changes
from utilities import return_closest

import sys

def main():
	days_back = int(sys.argv[1])
	max_items = int(sys.argv[2])
	if sys.argv[3].title() == 'True':
		percentage = True
	else:
		percentage = False
	plot_changes(days_back, 'potential market', max_items=max_items, start_item=0, percentage=percentage, interval=1, active_only=True)

if __name__ == '__main__':
  main()


#1. DONE! GET PLOT FOR NUMBER OF CAMPS IN META TRACKING CATEGORIES (OVERALL IN 'POTENTIAL MARKETS' AND EACH POTENTIAL MARKET, FOR EXAMPLE)
#2. SETUP OPTION FOR PLOTS TO SAVE TO CERTAIN FOLDER IN OLD_DATA
#2b. OPTION TO EXPORT RAW PLOT DATA TO A LOG FILE
#3. BUILD OUT OTHER PLOT FUNCTIONS
#4. DECIDE WHAT WOULD BE HELPFUL TO PLOT EVERY MONTH (MAYBE EVERY WEEK)
#5. WRITE A BASH SCRIPT TO RUN THE APPROPRIATE PLOTS FROM GENERATE_PLOT.PY FOR ABOVE
#6. ADD A MONTHLY OR WEEKLY CRONJOB TO RUN THIS SCRIPT AND STORE PLOTS IN AN OLD_DATA FOLDER OR SEPARATE DATA FOLDER