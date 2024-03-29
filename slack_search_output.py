import revised_search
from revised_search import Camp_Info
import utilities
from pprint import pprint
import sys
from current_data import attribute_dict
from slackbot.helpers import is_number

def title_string(camp, full=True):
	title_string = ''
	if full:
		title_string += '`' + ''.center((len(camp) + 10), '=') + '`\n'
	title_string += '`-----{}-----`\n\n'.format(camp)
	if full:
		title_string += '`' + ''.center((len(camp) + 10), '=') + '`\n\n\n'
	return title_string

def category_string(cat_data, camp, cat):
	cat_string = ''
	try:
		if cat in attribute_dict.Out_Dict.keys():
			cat_name = attribute_dict.Out_Dict[cat]
		else:
			cat_name = cat.title()
		cat_string += '*' + str(cat_name) + '*: '
		data_string = ''

		if type(cat_data) is list:
			data_string += '\n'
			for item in cat_data:
				data_string += '        ' + str(item) + ',\n'
			data_string = data_string[:-2]
			cat_string += data_string + '\n'
		elif cat == 'courses':
			data_string += '\n'
			for item in cat_data.keys():
				try:
					data_string += '        {} _(${})_,\n'.format(str(item), (cat_data[item]['Cost']/1))
				except (TypeError, KeyError):
					data_string += '        {},\n'.format(str(item))
			data_string = data_string[:-2]
			cat_string += data_string + '\n'
		elif type(cat_data) is dict:
			data_string += '\n'	
			if cat == 'employment_rates' or cat == 'matriculation_stats':
				er_ms_order = ['30 days', '60 days', '90 days', '120 days', '120+ days',
				'accepted', 'enrolled', 'graduated', 'job_seeking']
				for key in er_ms_order:
					if key in cat_data.keys():
						key_title = ' '.join(key.split('_'))
						if is_number(key[0:2]):
							data_string += '        {}: {}%\n'.format(key_title.title(),cat_data[key])
						else:
							data_string += '        {}: {}\n'.format(key_title.title(),cat_data[key])
			else:
				for k,v in cat_data.iteritems():
					data_string += '        {}: {}\n'.format(k,v)
			cat_string += data_string + '\n'
		elif cat == 'acceptance_rate':
			cat_string += str(cat_data) + '%\n'
		else:
			cat_string += str(cat_data) + '\n'
		
	except UnicodeError:
		return -1, -1

	return cat_string, cat_name

class Slack_Output_Strings:
	def __init__(self, bootcamps_out=None, details_out=None, list_out=None, sort_out=None, summary_out=None, warnings_out=None):
		self.bootcamps_out = bootcamps_out
		self.details_out = details_out
		self.list_out = list_out
		self.sort_out = sort_out
		self.summary_out = summary_out
		self.warnings_out = warnings_out

#1. FINISH SUMMARY OUTPUT
#2. APPEND WARNINGS (MAYBE TO SEPARATE CLASS FIELD) TO OUTPUT STRING OBJECT

def slack_output(result_data):
	return_strings = Slack_Output_Strings()

	non_display_list = ['cr_technologies', 'su_technologies', 'subjects', 'average_salary', 'top_source',
	'general_cost', 'name', 'cost_estimate', 'tracks']
	ordered_display_list = [
	['Number Of Locations', 'Locations', 'Number Of Courses', 'Courses', 'Average Course Cost', 'Technologies'],
	['Housing', 'Visas', 'Job Guarantee', 'Accreditation', 'Scholarships', 'Number Of Alumni'],
	['Hiring Rate', 'Class Ratio', 'Acceptance Rate', 'Employment Rates', 'Matriculation Stats'],
	['Website', 'Email', 'Twitter', 'Facebook'],
	['Course Report Reviews', 'Course Report Rating', 'Switchup Reviews', 'Switchup Rating'],
	['Last Updated', 'Tracking Groups']
	]

	#=========================BOOTCAMP PRINT=========================

	bootcamps_string = '\n\n'
	for camp in result_data.bootcamp_data:
		
		cost_list = []
		try:
			for course in result_data.bootcamp_data[camp]['courses']:
				try:
					cost = result_data.bootcamp_data[camp]['courses'][course]['Cost']
					if cost > 0:
						cost_list.append(cost)
				except KeyError:
					pass
		except KeyError:
			pass

		try:
			course_costs = '${}'.format(str(int(sum(cost_list)/float(len(cost_list)))))
			result_data.bootcamp_data[camp]['Average Course Cost'] = course_costs
		except ZeroDivisionError:
			pass

		bootcamps_string += title_string(camp)
		
		cstrings = {}

		for cat in result_data.bootcamp_data[camp]:
			if cat in non_display_list:
				continue
			cat_data = result_data.bootcamp_data[camp][cat]
			cat_string, cat_name = category_string(cat_data, camp, cat)
			if cat_string != -1:
				cstrings[cat_name] = cat_string

		for section in ordered_display_list:
			for dcat in section:
				if dcat in cstrings.keys():
					bootcamps_string += cstrings[dcat]
			bootcamps_string += '\n-----------------------\n'

		bootcamps_string = bootcamps_string[:-25] + '\n\n'
	return_strings.bootcamps_out = bootcamps_string

	#======================CATEGORY/DETAIL PRINT======================

	detail_string = '\n\n'
	for camp in result_data.camp_list:
		if len(result_data.category_data[camp]) == 0:
			continue
		detail_string += title_string(camp, full=False)
		for tup in result_data.category_data[camp]:
			cat_string, cat_name = category_string(tup[1], camp, tup[0])
			if cat_string != -1:
				detail_string += cat_string
		detail_string += '\n\n\n'
	return_strings.details_out = detail_string

	#===========================LIST PRINT============================


	camp_list_string = '`=========================================================`\n' 
	camp_list_string += '`List`: These bootcamps fit the group/location/technology filters (Camps in Search: {})'.format(str(len(result_data.camps)))
	camp_list_string += '\n`=========================================================`\n\n' 
	if len(result_data.camp_list) == 0:
		camp_list_string = -1
	else:
		for camp in result_data.camp_list:
			camp_list_string += '            ' + str(camp) + '\n'
	return_strings.list_out = camp_list_string

	#===========================SORT PRINT============================

	sort_list_string = '`===================================================`\n' 
	sort_list_string += '`SORT`: Sorted list of camps by specified categories'
	sort_list_string += '\n`===================================================`\n\n' 
	for item in result_data.sort.keys():
		category = result_data.sort[item]
		if item == 'warning':
			continue
		if item in attribute_dict.Out_Dict:
			item_title = attribute_dict.Out_Dict[item].title()
		else:
			item_title = item.title()
		sort_list_string += '*' + str(item_title) + '*\n----------------------------\n'
		for x in category:
			#list_string = '{:<30}{}'.format((str(x[0]) + ':'), str(x[1]))
			try:
				list_string = '            ' + str(x[0]) + ': ' + str(x[1])
			except UnicodeError:
				continue
			sort_list_string += list_string + '\n'
		sort_list_string += '\n\n'
	return_strings.sort_out = sort_list_string

	#==========================SUMMARY PRINT==========================

	summary_list_string = '`=========================================================`\n' 
	summary_list_string += '`SUMMARY`: Breakdown of specified categories (Camps in Search: {})'.format(str(len(result_data.camps)))
	summary_list_string += '\n`=========================================================`\n\n' 
	for item in result_data.summary.keys():
		category = result_data.summary[item]
		if item == 'warning':
			continue
		if item in attribute_dict.Out_Dict:
			item_title = attribute_dict.Out_Dict[item].title()
		else:
			item_title = item.title()
		summary_list_string += '*' + str(item_title) + '*\n----------------------------\n'
		category_sorted = sorted([[k,v] for k,v in category.iteritems()], key=lambda x: x[1], reverse=True)
		"""for k,v in category.iteritems():
			list_string = '            ' + str(k) + ': ' + str(v)
			summary_list_string += list_string + '\n'"""
		for x in category_sorted:
			try:
				list_string = '            ' + str(x[0]) + ': ' + str(x[1])
			except UnicodeError:
				continue
			summary_list_string += list_string + '\n'
		summary_list_string += '\n\n'
	return_strings.summary_out = summary_list_string

	#==========================WARNING PRINT==========================

	if result_data.summary['warning'] and len(result_data.summary['warning'][0][1]) > 0: 
		warning_list_string = '`WARNING: These camps fit the specified filters, but did not have data for the following categories`: \n\n'
		for cat in result_data.summary['warning']:
			if cat[0] in attribute_dict.Out_Dict.keys():
				cat_name = attribute_dict.Out_Dict[cat[0]]
			else:
				cat_name = cat[0].title()
			warning_list_string += '*{}*: '.format(cat_name)
			for camp in cat[1]:
				warning_list_string += str(camp) + ', '
			warning_list_string = warning_list_string[:-2]  +'\n'
			warning_list_string += '\n\n'
		return_strings.warnings_out = warning_list_string

	return return_strings

if __name__ == '__slack_output__':
    slack_output(result_data)