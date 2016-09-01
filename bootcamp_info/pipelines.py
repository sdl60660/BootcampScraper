3# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.exceptions import DropItem

class BootcampInfoPipeline(object):    

    def process_item(self, item, spider):
        if item['sources'][0] == 'CourseReport':
            dropped = False

            try:
                if item['facebook']:
                    pass
            except KeyError:
                drop_string = "Had not yet filled the facebook response field: " + str(item['name'])
                raise DropItem(drop_string)
                dropped = True
        
            try:
                if item['twitter']:
                    pass
            except KeyError:
                drop_string = "Had not yet filled the twitter response field: " + str(item['name'])
                raise DropItem(drop_string)
                dropped = True
        
            if dropped == False:
                return item
        else:
            return item

class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        name_source = str(item['name']) + str(item['sources'][0])
        if name_source in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(name_source)
            return item



class TrackingGroupTags(object):
    
    def process_item(self, item, spider):

        #This is completely subject to change, just needed to put in a few to test out the pipeline
        top_camps = ['hack reactor', 'the iron yard', 'general assembly', 'ironhack', 'dev bootcamp']
        current_markets = ['cleveland', 'columbus']
        potential_markets = ['cincinnati', 'pittsburgh', 'detroit', 'buffalo', 'toronto']
        #add list of top Java/.NET, check for thse while iterating through camp names (first loop)
        #general tag for all Java/.NET

        for camp in top_camps:
            if item['name'].title() == camp.title():
                item['tracking_groups'].append('Top Camp')

        try:
            for loc in item['locations']:
                for city in current_markets:
                    if city.title() == loc.title():
                        if city.title() not in item['tracking_groups']:
                            item['tracking_groups'].append(city.title())
                        if 'Current Market' not in item['tracking_groups']:
                            item['tracking_groups'].append('Current Market')
                for city in potential_markets:
                    if city.title() == loc.title():
                        if city.title() not in item['tracking_groups']:
                            item['tracking_groups'].append(city.title())
                        if 'Potential Market' not in item['tracking_groups']:
                            item['tracking_groups'].append('Potential Market')

        except TypeError:
            pass
        
        return item
                   

class EmptyChecker(object):
    
    def process_item(self, item, spider):
        if len(item['name']) == 0:
            raise DropItem("No name value!")
        else:
            return item





###=======EXAMPLE FROM DIRBOT=======###

"""
from scrapy.exceptions import DropItem


class FilterWordsPipeline(object):
    #A pipeline for filtering out items which contain certain words in their
    #description

    # put all words in lowercase
    words_to_filter = ['politics', 'religion']

    def process_item(self, item, spider):
        for word in self.words_to_filter:
            if word in unicode(item['description']).lower():
                raise DropItem("Contains forbidden word: %s" % word)
        else:
            return item
"""