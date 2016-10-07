import sys
import tracking
from tracking import tracked_camp_changes

def compact_duplicates(in_tuples):
	changed_camps = list(set([(c[1], c[2], None) for c in in_tuples]))
	for i,c in enumerate(changed_camps):
		set_string = ''
		for x in in_tuples:
			if (x[1], x[2]) == (c[0], c[1]):
				set_string += str(x[0]) + ', '
		set_string = set_string[:-2]
		changed_camps[i] = [set_string, c[0], c[1]]
	return changed_camps

def location_changes(result):
	#result = tracked_camp_changes(10, 'locations')
	print_list = []
	if len(result) > 0:
		changed_camps = compact_duplicates(result)

		for x in changed_camps:
			if x[0] == 'Online':
				print_list.append('{0} has {1} teaching {2}'.format(x[1], ('started' if x[2] == 'Addition' else 'stopped'), x[0]))
			else:
				print_list.append('{0} has moved {1} {2}'.format(x[1], ('into' if x[2] == 'Addition' else 'out of'), x[0]))
		return print_list
	else:
		return -1

def technology_changes(result):
	#result = tracked_camp_changes(10, 'locations')
	print_list = []
	if len(result) > 0:
		changed_camps = compact_duplicates(result)

		for x in changed_camps:
			print_list.append('{0} has {1} {2}'.format(x[1], ('started teaching' if x[2] == 'Addition' else 'stopped teaching'), x[0]))
		return print_list
	else:
		return -1

"""if __name__ == '__main__':
  main(result)"""