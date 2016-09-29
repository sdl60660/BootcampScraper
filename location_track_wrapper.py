import sys
import tracking
from tracking import tracked_camp_changes

def main():
	result = tracked_camp_changes(10, 'locations')
	print_list = []
	if len(result) > 0:
		for x in result:
			print_list.append('{0} has moved {1} {2}'.format(x[1], ('into' if x[2] == 'Addition' else 'out of'), x[0]))
		return print_list
	else:
		return -1

if __name__ == '__main__':
  main()