import psycopg2, json
from psycopg2.extensions import AsIs
from pprint import pprint
import re

def format_col(col_array):
	return str(col_array).strip('[]').replace(", u'", ", ").replace("', ", ", ").strip("u'")

def format_val(val_array):
	val_array = str(val_array).strip('[]').replace('"', "'").replace("u'Yes'", "TRUE").replace("u'No'", "FALSE").replace(", u'", ", '").strip("u")
	apostrophes = re.findall(r"[a-zA-Z]'[a-zA-Z]", val_array)
	for apost in apostrophes:
		val_array = val_array.replace(apost, (apost[0] + "''" + apost[-1]))
	return val_array

datafile = open('current_data/output.json', 'rU')
current_data = json.load(datafile)
bootcamps = [current_data[x] for x in current_data.keys() if x != 'meta']
# pprint(bootcamps[42])
# pprint(current_data)

conn = psycopg2.connect("dbname=bootcamps user=samlearner")
cur = conn.cursor()

for camp in bootcamps:
	cur.execute("SELECT * FROM school;")
	school_fields = [desc[0] for desc in cur.description]
	# print cur.description

	columns = [x for x in camp.keys() if type(camp[x]) not in {list, dict} and x in school_fields and camp[x]]
	values = [camp[x] for x in camp.keys() if type(camp[x]) not in {list, dict} and x in school_fields and camp[x]]

	for v, val in enumerate(values):
		if type(val) in {str, unicode}:
			values[v] = val.replace(" '", " ''").replace("' ", "'' ").replace(' "', " ''").replace('" ', "'' ").replace(' \"', " ''").replace('\" ', "'' ")

	columns, values = format_col(columns), format_val(values)

	# print columns, values

	data = (AsIs(columns), AsIs(values))
	sql_statement = "INSERT INTO school (%s) VALUES (%s);" % data
	print sql_statement
	
	# print sql_statement
	# print cur.mogrify(sql_statement, (columns, values))
	#try:
	cur.execute(sql_statement) #, data)
	#except psycopg2.ProgrammingError:
	#	print sql_statement
cur.close()
conn.commit()
conn.close()

# cur.execute("SELECT * FROM location;")

# a = cur.fetchone()
# print a