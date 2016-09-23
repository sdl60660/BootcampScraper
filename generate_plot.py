import tracking
from tracking import tracking_groups

from tracking import plot_changes
from utilities import return_closest

import sys

def main():
	plot_changes(15, 'technologies', max_items=10, start_item=10, show_legend=False)

if __name__ == '__main__':
  main()