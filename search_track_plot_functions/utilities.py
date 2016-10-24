
def return_closest(query, search_set, threshold=0.7):
    from difflib import SequenceMatcher
    closest = (None, 0.0)
    for term in search_set:
        if type(term) == tuple:
            match = SequenceMatcher(None, query.lower(), term[0].lower()).ratio()
        else:
            match = SequenceMatcher(None, query.lower(), term.lower()).ratio()
        if match > closest[1]:
            closest = (term, match)
    if closest[1] < threshold:
        """print
        print 'Sorry! Your search term "' + str(query) + '" did not return a close enough match with any search terms. It may not be in the dataset.'
        print"""
        return -1
    #print closest
    return closest[0]


def dict_print(in_dict, title):
    import operator
    from pprint import pprint
    print title.title() + ':'
    tuple_list = []

    for k,v in in_dict.iteritems():
        tuple_list.append((k, v))
        val_type = type(v)
 
    if val_type == int or val_type == float:
        tuple_list = sorted(tuple_list, key=operator.itemgetter(1), reverse=True)
    elif val_type == list:
        tuple_list = sorted(tuple_list, key=lambda tup: len(tup[1]), reverse=True)
    else:
        tuple_list = sorted(tuple_list, key=operator.itemgetter(1), reverse=False)
    
    for tup in tuple_list:
        if val_type == list:
            print_string = unicode(tup[0])+ ': ' + unicode(len(tup[1]))
        else:
            print_string = unicode(tup[0])+ ': ' + unicode(tup[1])
        pprint(print_string, indent=4)
    print
    return