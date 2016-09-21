
from difflib import SequenceMatcher

def return_closest(query, search_set, threshold):
    closest = (None, 0.0)
    for term in search_set:
        if type(term) == tuple:
            match = SequenceMatcher(None, query.lower(), term[0].lower()).ratio()
        else:
            match = SequenceMatcher(None, query.lower(), term.lower()).ratio()
        if match > closest[1]:
            closest = (term, match)
    if closest[1] < threshold:
        print
        print 'Sorry! Your search term "' + str(query) + '" did not return a close enough match with any search terms. It may not be in the dataset.'
        print
        return -1
    #print closest
    return closest[0]