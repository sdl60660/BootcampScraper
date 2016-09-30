import revised_search
from revised_search import Camp_Info
import utilities
from pprint import pprint
import sys
from current_data import attribute_dict


"""class Camp_Info:
    def __init__(self, category_data, camps, summary=None, camp_list=None, sort=None):
        self.category_data = category_data
        self.camps = camps
        self.summary = summary if summary is not None else []
        self.camp_list = camp_list if camp_list is not None else []
        self.sort = sort if sort is not None else []"""
class Slack_Output_Strings:
	def __init__(self, list_out=None, sort_out=None, summary_out=None, category_out=None):
		self.list_out = list_out
		self.sort_out = sort_out
		self.summary_out = summary_out
		self.category_out = category_out

#1. FINISH SUMMARY OUTPUT
#2. APPEND WARNINGS (MAYBE TO SEPARATE CLASS FIELD) TO OUTPUT STRING OBJECT
#3. PACKAGE AND RETURN STRING SO THAT BOT NO LONGER HAS TO GO THROUGH TEMRINAL

def slack_output(result_data):
	return_strings = Slack_Output_Strings()

	camp_list_string = '==================================================\n' 
	camp_list_string += 'LIST: These bootcamps fit the inputed tracking group, location, and technology filters (Total Camps in Search: ' + str(len(result_data.camps)) + ')\n'
	camp_list_string += '==================================================\n\n' 
	for camp in result_data.camp_list:
		camp_list_string += '            ' + str(camp) + '\n'
	return_strings.list_out = camp_list_string

	sort_list_string = '==================================================\n' 
	sort_list_string += 'SORT: Sorted list of camps by specified categories\n'
	sort_list_string += '==================================================\n\n' 
	for item in result_data.sort.keys():
		category = result_data.sort[item]
		if item == 'warning':
			continue
		sort_list_string += str(item).title() + '\n----------------------------\n'
		for x in category:
			#list_string = '{:<30}{}'.format((str(x[0]) + ':'), str(x[1]))
			list_string = '            ' + str(x[0]) + ': ' + str(x[1])
			sort_list_string += list_string + '\n'
		sort_list_string += '\n\n'
	return_strings.sort_out = sort_list_string

	summary_list_string = '==================================================\n' 
	summary_list_string += 'SUMMARY: Breakdown of specified categories (Total Camps in Search: ' + str(len(result_data.camps)) + ')\n'
	summary_list_string += '==================================================\n\n' 
	for item in result_data.summary.keys():
		category = result_data.summary[item]
		if item == 'warning':
			continue
		summary_list_string += str(item).title() + '\n----------------------------\n'
		category_sorted = sorted([[k,v] for k,v in category.iteritems()], key=lambda x: x[1], reverse=True)
		"""for k,v in category.iteritems():
			list_string = '            ' + str(k) + ': ' + str(v)
			summary_list_string += list_string + '\n'"""
		for x in category_sorted:
			list_string = '            ' + str(x[0]) + ': ' + str(x[1])
			summary_list_string += list_string + '\n'
		summary_list_string += '\n\n'

	print
	print camp_list_string
	print
	print sort_list_string
	print
	print summary_list_string


if __name__ == '__slack_output__':
    slack_output(result_data)