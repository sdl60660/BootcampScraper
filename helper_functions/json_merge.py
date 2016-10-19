import json
from jsonmerge import merge
from jsonmerge import Merger
import sys
from pprint import pprint

import datetime

def create_meta_dict(date_time, output_dict):
    meta_dict = {}

    meta_dict['Date/Time'] = str(date_time)[:19]
    meta_dict['Days Out'] = date_time.toordinal() - 736219
    meta_dict['Number of Entries'] = len(output_dict)

    meta_dict['Current Market'] = list()
    meta_dict['Potential Market'] = list()

    meta_dict['Cleveland'] = list()
    meta_dict['Columbus'] = list()
    meta_dict['Pittsburgh'] = list()
    meta_dict['Cincinnati'] = list()
    meta_dict['Buffalo'] = list()
    meta_dict['Detroit'] = list()
    meta_dict['Toronto'] = list()

    if meta_dict['Days Out'] < 0:
        meta_dict['Active'] = False
    else:
        meta_dict['Active'] = True

    tech_dict = {}
    loc_dict = {}

    for name in output_dict:
        for group in range(len(output_dict[name]['tracking_groups'])):
            try:
                meta_dict[output_dict[name]['tracking_groups'][group]].append(output_dict[name]['name'])
            except KeyError:
                pass
                
        try:
            for loc in output_dict[name]['locations']:
                if loc in loc_dict:
                    loc_dict[loc] += 1
                else:
                    if len(loc) > 1:
                        loc_dict[loc] = 1
        except (KeyError, TypeError):
            pass

        try:
            for tech in output_dict[name]['technologies']:

                if tech in tech_dict:
                    tech_dict[tech] += 1
                else:
                    if tech not in loc_dict:
                        tech_dict[tech] = 1
        except (KeyError, TypeError):
            pass

    meta_dict['technologies'] = tech_dict
    meta_dict['locations'] = loc_dict

    return meta_dict

def main():

    #check if the optional output flag was included
    #if so, the last filename is the output file
    output = False

    for arg in range(len(sys.argv)):
        if sys.argv[arg] == '--output':
            output = True
            sys.argv.remove('--output')
            break

    if output == True:
        output_file = sys.argv[-1]
        file_array = sys.argv[:-1]
    else:
        output_file = 'output.json'
        file_array = sys.argv


    #create an array to store json files from spiders
    json_files = []

    #add json files from scraper directory, specified in command line
    for i in range(1, len(file_array)):
        json_files.append(file_array[i])

    #create dictionary of numbered keys to bootcamps json files
    bootcamp_data = {}
    key_num = 0

    #load json files
    for file in json_files:
        key_num += 1
        with open(file) as json_data:
            bootcamp_data[key_num] = json.load(json_data)

    num_similar = 0

    output_dict = {}

    #merge each file included in argument list, with later ones taking conflict priority
    for file in bootcamp_data:
        try:
            for x in bootcamp_data[file]:
                try:
                    name = str(bootcamp_data[file][x]['name']).title()
                    if name in output_dict:
                        temp_item = output_dict[name]
                        output_dict[name] = merge(output_dict[name], bootcamp_data[file][x])

                        #JUST IN CASE A TRACKING GROUP WAS MARKED ON ONE SOURCE
                        #AND NOT ANOTHER AND THEN MISSED BECAUSE OF THE MERGE
                        output_dict[name]['tracking_groups'] = []

                        for group in bootcamp_data[file][x]['tracking_groups']:
                            output_dict[name]['tracking_groups'].append(group)
                        for group in temp_item['tracking_groups']:
                            if group not in bootcamp_data[file][x]['tracking_groups']:
                                output_dict[name]['tracking_groups'].append(group)

                        try:
                            for course in bootcamp_data[file][x]['courses'].keys():
                                if course in temp_item['courses'].keys():
                                    output_dict[name]['courses'][course] = merge(temp_item['courses'][course], bootcamp_data[file][x]['courses'][course])
                        except KeyError:
                            pass
                    else:
                        output_dict[name] = bootcamp_data[file][x]
                except KeyError:
                    pass

        except TypeError:
            for x in range(len(bootcamp_data[file])):
                name = str(bootcamp_data[file][x]['name']).title()
                if name in output_dict:
                    temp_item = output_dict[name]
                    output_dict[name] = merge(output_dict[name], bootcamp_data[file][x])

                    #JUST IN CASE A TRACKING GROUP WAS MARKED ON ONE SOURCE
                    #AND NOT ANOTHER AND THEN MISSED BECAUSE OF THE MERGE
                    output_dict[name]['tracking_groups'] = []

                    for group in bootcamp_data[file][x]['tracking_groups']:
                        output_dict[name]['tracking_groups'].append(group)
                    for group in temp_item['tracking_groups']:
                        if group not in bootcamp_data[file][x]['tracking_groups']:
                            output_dict[name]['tracking_groups'].append(group)

                    try:
                        for course in bootcamp_data[file][x]['courses'].keys():
                            if course in temp_item['courses'].keys():
                                output_dict[name]['courses'][course] = merge(temp_item['courses'][course], bootcamp_data[file][x]['courses'][course])
                    except KeyError:
                        pass
                else:
                    output_dict[name] = bootcamp_data[file][x]

    #MERGE TECHNOLOGIES FROM DIFFERENT REPORTING SOURCES AND REPLACE TECHNOLOGIES LIST FOR EACH BOOTCAMP
    for name in output_dict:
        new_technologies = []
        try:
            for tech in output_dict[name]['su_technologies']:
                if tech not in new_technologies:
                    new_technologies.append(tech)
        except (KeyError, TypeError):
            pass

        try:
            for tech in output_dict[name]['cr_technologies']:
                if tech not in new_technologies:
                    new_technologies.append(tech)
        except (KeyError, TypeError):
            pass

        try:
            output_dict[name]['technologies'] = new_technologies
        except (KeyError, TypeError):
            pass


    #STORE META DATA ON THE OUTPUT JSON
    now = datetime.datetime.now()
    output_dict['meta'] = create_meta_dict(now, output_dict)


    #write merge JSON to output file
    with open(output_file, 'w') as f:
        json.dump(output_dict, f, indent=4, sort_keys=True)

    file_print_array = []
    for f, file in enumerate(file_array):
        temp = ((file_array[f].split('/'))[-1])
        temp = ' '.join(((temp.split('.'))[0]).split('_'))
        file_print_array.append(temp.title())


    print
    print "========================================"
    print "================SUMMARY================="
    print "========================================"
    print
    print
    for file in bootcamp_data:
        print "Total JSON items in " + str(file_print_array[file]) + ": " + str(len(bootcamp_data[file]))
    print
    print "Total in OUTPUT: " + str(len(output_dict))
    print
    """print "Total Similar: " + str(num_similar)
    """
if __name__ == '__main__':
    main()