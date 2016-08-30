import json
from jsonmerge import merge
from jsonmerge import Merger
import sys
from pprint import pprint

from scrapy.mail import MailSender

mailer = MailSender()

if len(sys.argv) == 3:
    file = sys.argv[1]
    key = str(sys.argv[2]).title()
elif len(sys.argv) == 2:
    file = 'current_data/output.json'
    key = str(sys.argv[1]).title()

with open(file) as json_data:
    bootcamps = json.load(json_data)

print
print
print "============================================================"
print "         INFORMATION FOR BOOTCAMP: " + key
print "============================================================"
print
try:
    pprint(bootcamps[key], width=50)
except KeyError:
    print "Sorry! " + str(key) + " not found. Check for spelling or name variations."
print
print

#email_subject = key.title() + ' Information'
#email_body = str(bootcamps[key])

#mailer.send(to=['sam@techelevator.com'], subject=email_subject, body=email_body)


print "ALSO! (temporarily) Here are some stats on technology usage and bootcamp reviews:"
print

tech_dict = {}

for bootcamp in bootcamps:

    try:
        for technology in bootcamps[bootcamp]['technologies']:
            if technology in tech_dict:
                tech_dict[technology] += 1
            else:
                tech_dict[technology] = 1
    except (KeyError, TypeError):
        pass
        #if technology in tech_dict:
         #   tech_dict[technology] += 1
        #else:
        #    tech_dict[technology] = 1

sort_dict = sorted(tech_dict, key=tech_dict.get, reverse=True)

for item in sort_dict:
    if len(item) > 1 or item == 'R' or item == 'C':
        print str(item) + ": " + str(tech_dict[item])

print
print

review_dict = {}

for bootcamp in bootcamps:
    try:
        review_dict[bootcamps[bootcamp]['name']] = bootcamps[bootcamp]['twitter']['followers']
    except (KeyError, TypeError):
        pass

sort_dict = sorted(review_dict, key=review_dict.get, reverse=True)

for item in sort_dict:
    print str(item) + ': ' + str(review_dict[item])

print


#pprint (sorted(tech_dict, key=tech_dict.get, reverse=True), width=50)