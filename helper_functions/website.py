import webbrowser
from difflib import SequenceMatcher
import sys
import json

bootcamp = sys.argv[1]
bcdata = open('current_data/output.json', 'r')
bootcamps = json.load(bcdata)

camp_match = None
top_match = 0.7
found = False
for camp in bootcamps:
    ratio = SequenceMatcher(None, camp, bootcamp).ratio()
    if ratio > top_match:
        top_match = ratio
        camp_match = camp
        found = True

if found == False:
    print 'No matching bootcamp was found. It may not be in the dataset, or it may be badly misspelled. Exiting...'
    sys.exit()

if camp_match:
    try:
        website = bootcamps[camp_match]['website']
        if website:
            print website
            webbrowser.open(website)
    except KeyError:
        print 'No website found for bootcamp: ' + str(camp_match) + '.'
        sys.exit()
    