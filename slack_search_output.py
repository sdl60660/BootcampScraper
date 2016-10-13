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
	def __init__(self, bootcamps_out=None, details_out=None, list_out=None, sort_out=None, summary_out=None):
		self.bootcamps_out = bootcamps_out
		self.details_out = details_out
		self.list_out = list_out
		self.sort_out = sort_out
		self.summary_out = summary_out

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

		bootcamps_string += '`' + ''.center((len(camp) + 10), '=') + '`\n'
		bootcamps_string += '`-----{}-----`\n\n'.format(camp)
		bootcamps_string += '`' + ''.center((len(camp) + 10), '=') + '`\n\n\n'
		
		cstrings = {}

		for cat in result_data.bootcamp_data[camp]:
			cat_string = ''
			try:
				if cat in non_display_list:
					continue
				if cat in attribute_dict.Out_Dict.keys():
					cat_name = attribute_dict.Out_Dict[cat]
				else:
					cat_name = cat.title()
				cat_string += '*' + str(cat_name) + '*: '
				cat_data = result_data.bootcamp_data[camp][cat]
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
								data_string += '        {}: {}%\n'.format(key.title(),cat_data[key])
					else:
						for k,v in cat_data.iteritems():
							data_string += '        {}: {}\n'.format(k,v)
					cat_string += data_string + '\n'
				else:
					cat_string += str(cat_data) + '\n'
				cstrings[cat_name] = cat_string
			except UnicodeError:
				pass

		for section in ordered_display_list:
			for dcat in section:
				if dcat in cstrings.keys():
					bootcamps_string += cstrings[dcat]
			bootcamps_string += '\n-----------------------\n'

		bootcamps_string = bootcamps_string[:-25] + '\n\n'
	return_strings.bootcamps_out = bootcamps_string

	pprint(result_data.category_data)


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
		if item in attribute_dict.Out_Dict:
			item_title = attribute_dict.Out_Dict[item].title()
		else:
			item_title = item.title()
		sort_list_string += str(item_title) + '\n----------------------------\n'
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
		if item in attribute_dict.Out_Dict:
			item_title = attribute_dict.Out_Dict[item].title()
		else:
			item_title = item.title()
		summary_list_string += str(item_title) + '\n----------------------------\n'
		category_sorted = sorted([[k,v] for k,v in category.iteritems()], key=lambda x: x[1], reverse=True)
		"""for k,v in category.iteritems():
			list_string = '            ' + str(k) + ': ' + str(v)
			summary_list_string += list_string + '\n'"""
		for x in category_sorted:
			list_string = '            ' + str(x[0]) + ': ' + str(x[1])
			summary_list_string += list_string + '\n'
		summary_list_string += '\n\n'
	return_strings.summary_out = summary_list_string
	return return_strings

if __name__ == '__slack_output__':
    slack_output(result_data)