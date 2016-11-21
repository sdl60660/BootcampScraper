# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.exceptions import DropItem

import csv
from difflib import SequenceMatcher

selected_camps = []
with open('old_data/selected_camps.csv', 'r') as selected_camp_list:
    sc_list = csv.reader(selected_camp_list, delimiter=',')
    for item in sc_list:
        selected_camps.append(item)
selected_camps = selected_camps[0]

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

        if item['name'].title() == 'The Software Guild':
            item['name'] = 'Software Guild'

        if item['name'].title() == 'Eleven Fifty Academy':
            item['name'] = 'Eleven Fifty Coding Academy'

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

        if item['name'].title() == 'New York Code And Design Academy':
            item['name'] = 'New York Code + Design Academy'
        
        return item

class TechnologyListingFixes(object):

    def process_item(self, item, spider):
        caught_issues = ['2016', 'September 30', 'Rolling Dates', 'October 18', 'NYC', 'January  9', '2017']
        fields = ['technologies', 'cr_technologies', 'su_technologies']

        for field in fields:
            try:
                for i, tech in enumerate(item[field]):
                    if tech == 'Javascript':
                        item[field][i] = 'JavaScript'
                    if tech == 'Rails':
                        item[field][i] = 'Ruby on Rails'
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

        try:
            for c, course in enumerate(item['courses']):
                for i, tech in enumerate(course['Subjects']):
                    if tech == 'Javascript':
                        item['courses'][i] = 'JavaScript'
                    if tech == 'Rails':
                        item['courses'][i] = 'Ruby on Rails'
                    if tech == 'Express':
                        item['courses'][i] = 'Express.js'
                    if tech == 'Product Mgmt':
                        item['courses'][i] = 'Product Management'
                    if tech[0:10] == 'SharePoint':
                        item['courses'][i] = 'SharePoint'
                    if tech[-1] == ' ':
                        item['courses'][i] = tech[:-1]
                    if tech in caught_issues:
                        item['courses'].remove(tech)
        except (KeyError, TypeError):
            pass

        return item

class LocationFixes(object):

    def process_item(self, item, spider):
        #caught_issues = []
        #fields = ['technologies', 'cr_technologies', 'su_technologies']

        try:
            for l, loc in enumerate(item['locations']):
                if loc == 'NYC':
                    item['locations'][l] = 'New York City'
                if loc == 'St.Louis':
                    item['locations'][l] = 'St. Louis'
                if loc == 'Pheonix':
                    item['locations'][l] = 'Phoenix'
                if loc == 'Ottowa':
                    item['locations'][l] = 'Ottawa'
        except (KeyError, TypeError):
            pass

        try:
            for c, course in enumerate(item['courses']):
                for l, loc in enumerate(course['Location']):
                    if loc == 'NYC':
                        course['Location'][l] = 'New York City'
                    if loc == 'St.Louis':
                        course['Location'][l] = 'St. Louis'
                    if loc == 'Pheonix':
                        course['Location'][l] = 'Phoenix'
                    if loc == 'Ottowa':
                        course['Location'][l] = 'Ottawa'
        except (KeyError, TypeError):
            pass

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
        top_camps = ['hack reactor', 'the iron yard', 'general assembly', 'ironhack', 'dev bootcamp', 'flatiron school']
        current_markets = ['cleveland', 'columbus']
        potential_markets = ['cincinnati', 'pittsburgh', 'detroit', 'buffalo', 'toronto']
        java_and_net = ['Claim Academy', 'Coder Camps', 'Coder Foundry', 'Code Ninja', 'Coding Temple', 'Devcodecamp', 'Epicodus', 'Fire Bootcamp', 'Grand Circus', 'Sabio', 'Skill Distillery', 'Software Guild', 'The Iron Yard', 'The Tech Academy']

        for camp in top_camps:
            if item['name'].title() == camp.title():
                if 'Top Camp' not in item['tracking_groups']:
                    item['tracking_groups'].append('Top Camp')

        for camp in selected_camps:
            if item['name'].title() == camp.title():
                if 'Selected Camp' not in item['tracking_groups']:
                    item['tracking_groups'].append('Selected Camp')
            elif (SequenceMatcher(None, item['name'].lower(), camp.lower()).ratio()) > 0.95:
                if 'Selected Camp' not in item['tracking_groups']:
                    item['tracking_groups'].append('Selected Camp')

        for camp in java_and_net:
            if item['name'].title() == camp.title():
                item['tracking_groups'].append('Java/.NET')

        try:
            for location in item['locations']:
                if location.lower() in current_markets:
                    if 'Current Market' not in item['tracking_groups']:
                        item['tracking_groups'].append('Current Market')
                elif location.lower() in potential_markets:
                    if 'Potential Market' not in item['tracking_groups']:
                        item['tracking_groups'].append('Potential Market')
        except TypeError:
            pass

        if len(item['tracking_groups']) > 0:
            item['tracking_groups'] = list(set(item['tracking_groups']))

        if item['name'].lower() == 'acadgild' or 'girl develop it':
            item['tracking_groups'] = []

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