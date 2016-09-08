import json
import sys

output_file = sys.argv[1]
with open (output_file, 'rb') as datafile:
    data = json.load(datafile)

tuple_array = []

for item1 in data:
    for item2 in data:
        if item1 != item2:
            try:
                if data[item1]['website'] == data[item2]['website']:
                    if len(data[item1]['website']) > 0:
                        if data[item1]['top_source'] != data[item2]['top_source']:
                            tuple_array.append(((item1, data[item1]['top_source']), (item2, data[item2]['top_source'])))
                            print data[item1]['website']
            except (KeyError, TypeError):
                pass

            try:
                if data[item1]['email'] == data[item2]['email']:
                    if len(data[item1]['email']) > 0:
                        if data[item1]['top_source'] != data[item2]['top_source']:
                            tuple_array.append(((item1, data[item1]['top_source']), (item2, data[item2]['top_source'])))
            except (KeyError, TypeError):
                pass

            """try:
                name1 = data[item1]['name']
                name2 = data[item2]['name']

                    tuple_array.append((item1, item2))
            except KeyError:
                pass"""

print

for item in tuple_array:
    if (item[1], item[0]) in tuple_array:
        tuple_array.remove(item)

for item in tuple_array:
    print item