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
                raise DropItem("Had not yet filled the facebook response field")
                dropped = True
        
            try:
                if item['twitter']:
                    pass
            except KeyError:
                raise DropItem("Had not yet filled the twitter response field")
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