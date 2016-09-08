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

class CaughtDuplicateNames(object):
    #FOUND SO FAR: Software Guild, HackSchool, Coder's Lab, Northwestern Coding Bootcamp, Gainesville Dev Academy
    #Helio Training Boocamp, Beach Coders Academy, Make School, Velocity 360, Ada Developers Academy, Founders & Coders

    def process_item(self, item, spider):
        if item['name'].title() == 'Software  Guild' or item['name'].title() == 'Software Craftsmanship Guild':
            item['name'] = 'Software Guild'

        if item['name'].title() == 'Hack School' or item['name'].title() == 'Hackschool':
            item['name'] = 'HackSchool'

        if item['name'].title() == "Coder'S Lab":
            item['name'] = 'Coders Lab'

        if item['name'].title() == 'Northwestern Coding Boot Camp':
            item['name'] = 'Northwestern Coding Bootcamp'

        if item['name'].title() == 'Gainsville Dev Academy':
            item['name'] = 'Gainesville Dev Academy'

        if item['name'].title() == 'Helio Training':
            item['name'] = 'Helio Training Bootcamp'

        if item['name'].title() == 'Beach Coders':
            item['name'] = 'Beach Coders Academy'

        if item['name'].title() == 'Makeschool':
            item['name'] = 'Make School'

        if item['name'].title() == 'Velocity':
            item['name'] = 'Velocity 360'

        if item['name'].title() == 'Ada':
            item['name'] = 'Ada Developers Academy'

        if item['name'].title() == 'Founders And Coders':
            item['name'] = 'Founders & Coders'
        
        return item

class TechnologyListingFixes(object):

    def process_item(self, item, spider):
        caught_issues = ['2016', 'September 30', 'Rolling Dates', 'October 18']
        fields = ['technologies', 'cr_technologies', 'su_technologies']

        for field in fields:
            try:
                for i, tech in enumerate(item[field]):
                    if tech == 'Javascript':
                        item[field][i] = 'JavaScript'
                    if tech == 'Express':
                        item[field][i] = 'Express.js'
                    if tech == 'Product Mgmt':
                        item[field][i] = 'Product Management'
                    if tech[0:10] == 'SharePoint':
                        item[field][i] = 'SharePoint'
                    if tech[-1] == ' ':
                        item[field][i] = tech[:-1]
                    if tech in caught_issues:
                        item[field].remove(tech)
            except (KeyError, TypeError):
                continue

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
        java_and_net = ['Claim Academy', 'Coder Camps', 'Coder Foundry', 'Code Ninja', 'Coding Temple', 'Devcodecamp', 'Epicodus', 'Fire Bootcamp', 'Grand Circus', 'Sabio', 'Skill Distillery', 'Software Guild', 'The Iron Yard', 'The Tech Academy']
        #add list of top Java/.NET, check for thse while iterating through camp names (first loop)
        #general tag for all Java/.NET

        for camp in top_camps:
            if item['name'].title() == camp.title():
                item['tracking_groups'].append('Top Camp')

        for camp in java_and_net:
            if item['name'].title() == camp.title():
                item['tracking_groups'].append('Java/.NET')

        try:
            for location in item['locations']:
                if location.lower() in current_markets:
                    if 'Current Market' not in item['tracking_groups']:
                        item['tracking_groups'].append('Current Market')
                    if location.title() not in item['tracking_groups']:
                        item['tracking_groups'].append(location.title())
                elif location.lower() in potential_markets:
                    if 'Potential Market' not in item['tracking_groups']:
                        item['tracking_groups'].append('Potential Market')
                    if location.title() not in item['tracking_groups']:
                        item['tracking_groups'].append(location.title())
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