# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

import datetime

import timestring

from scrapy import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import HtmlResponse, Response
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.linkextractors import LinkExtractor

from bootcamp_info.items import SwitchupSchool

#GLOBAL COUNTER

class SwitchupSpider(scrapy.Spider):
    bc_count = 0
    name = "switchup"
    allowed_domains = ["switchup.org"]
    start_urls = (
        'https://www.switchup.org/coding-bootcamps-reviews?mobile=false&page=1',
    )

    def parse(self, response):
        page_url = 'https://www.switchup.org/coding-bootcamps-reviews?mobile=false&page=1'
        yield scrapy.Request(page_url, callback=self.parse_schools)

    def parse_schools(self, response):
        #print response.text
        schools = Selector(response).xpath('//*[@class="topic-title"]/a/@href').extract()
        for school in schools:
            url_stub = school
            school_url = 'https://www.switchup.org' + url_stub
            yield scrapy.Request(school_url, callback=self.parse_contents)

        next_page = Selector(response).xpath('//*/div[@class="pagination"]/a[@rel="next"][@class="next_page"]/@href').extract()
        if next_page:
            url_stub = str(next_page)[3:-2]
            page_url = 'https://www.switchup.org' + url_stub
            print
            print "PAGE URL: " + str(page_url)
            print
            yield scrapy.Request(page_url, self.parse_schools)

    def parse_contents(self, response):
        item = SwitchupSchool()
        self.bc_count += 1

        #SCHOLARSHIPS, SUBJECTS, HIRING RATE, AVERAGE SALARY, NUMBER OF ALUMNI, CLASS RATIO

        #these are the 'lItems', they are the items I'm looking for a table index for, they'll will be keys for tItem indices
        item_list = ['Scholarships', 'Subject', 'Hiring %', 'Avg Salary', 'Alumni #', 'Class Ratio']
        #these are the 'tItems', they are the header names for the actual items in the webpage's table, will use to find table index on webpage
        table = Selector(response).xpath('//*[@id="bootcamp-summary"]/table/tbody/tr/th/text()').extract()
        item_index = {}

        for x, tItem in enumerate(table):
            for y, lItem in enumerate(item_list):
                if tItem == lItem:
                    item_index[lItem] = (x + 1)

        item['name'] = str(Selector(response).xpath('//*[@id="first-bootcamp-section"]/div/div/h1/text()').extract())[3:-2].title() #DONE
        item['locations'] = Selector(response).xpath('//*[@id="bootcamp-summary"]/table/tbody/tr[@itemprop="address"]/td[@itemprop="addressLocality"]/a/text()').extract() #DONE
        item['general_cost'] = Selector(response).xpath('//*[@id="bootcamp-summary"]/table/tbody/tr/td[@itemprop="priceRange"]/text()').extract() #DONE

        website_buffer = str(Selector(response).xpath('//*[@id="bootcamp-summary"]/table/tbody/tr/td/a[@class="website-link"]/@onclick').extract()) #DONE
        item['website'] = website_buffer[16:((website_buffer.find('); trackO') - 1))] #DONE

        scholarships = Selector(response).xpath('//*[@id="bootcamp-summary"]/table/tbody/tr/td/p/text()').extract()
        if len(scholarships) == 1:
            item['scholarships'] = scholarships
        #for x in item['scholarships']:
        #    if x[0:2] == '\n':
        #        item['scholarships'].remove(x)
        item['subjects'] = Selector(response).xpath(self.find_table_key('Subject', item_index)).extract()
        item['hiring_rate'] = Selector(response).xpath(self.find_table_key('Hiring %', item_index)).extract()
        item['average_salary'] = self.type_converter((Selector(response).xpath(self.find_table_key('Avg Salary', item_index)).extract()), int)
        item['num_alumni'] = self.type_converter((Selector(response).xpath(self.find_table_key('Alumni #', item_index)).extract()), int)
        item['class_ratio'] = Selector(response).xpath(self.find_table_key('Class Ratio', item_index)).extract()

        item['su_rating'] = self.type_converter((Selector(response).xpath('//*[@id="first-bootcamp-section"]/div/div/p/span[1]/span/text()').extract()), float) #DONE
        item['su_num_reviews'] = self.type_converter((Selector(response).xpath('//*[@id="first-bootcamp-section"]/div/div/p/span[2]/text()').extract()), int) #DONE


        #=========================================#
        #=================COURSES=================#
        #=========================================#
        courses = {}
        technologies = []

#=========================================================================================================#
#============================================IN PROGRESS BELOW============================================#
#=========================================================================================================#  


        if len(Selector(response).xpath('//h3[@class="course-name"]').extract()) > 0:
            
            course_info_headings = Selector(response).xpath('//table[@class="course-info"]/tbody/tr/th/text()').extract()
            course_info = Selector(response).xpath('//table[@class="course-info"]/tbody/tr/td/text()').extract()

            course_info_tags = Selector(response).xpath('//table[@class="course-info"]/tbody/tr/td').extract()

            if len(course_info) != len(course_info_tags):
                target_index = 0
                for table_item in course_info_tags:
                    target_index += 1
                    try:
                        if len(str(table_item)) == 9:
                            course_info.insert(target_index, 'N/A')
                    except UnicodeEncodeError:
                        pass


            index_tuples = []

            for h, heading in enumerate(course_info_headings):
                index_tuples.append((heading, course_info[h]))

            info_index = 0

            for x in range(len(Selector(response).xpath('//a[@class="course-listing"]/text()').extract())):
                course = {}
                name = Selector(response).xpath('//h3[@class="course-name"]/text()').extract()[x]
                name = ''.join([i if ord(i) < 128 else ' ' for i in name])
                course['Title'] = name

                info_index +=1

                try:
                    while index_tuples[info_index][0] != 'Description' and info_index < len(index_tuples):
                        if index_tuples[info_index][0] == 'Subjects':
                            subjects = index_tuples[info_index][1].split(', ')
                            course[index_tuples[info_index][0]] = subjects
                            for tech in subjects:
                                if tech not in technologies:
                                    technologies.append(tech)
                        elif index_tuples[info_index][0] == 'Location':
                            locations = list(index_tuples[info_index][1].split(', '))
                            course[index_tuples[info_index][0]] = locations
                        elif index_tuples[info_index][0] == 'Cost':
                            cost = int(''.join((str(index_tuples[info_index][1])[1:-3]).split(',')))
                            course[index_tuples[info_index][0]] = cost
                        elif index_tuples[info_index][0] == 'Class Size':
                            size = int(str(index_tuples[info_index][1])[:-9])
                            if size == 0:
                                course[index_tuples[info_index][0]] = None
                            else:
                                course[index_tuples[info_index][0]] = size
                        #COMMITMENT WILL END UP AS AN INT THAT REPRESENTS HOURS/WEEK
                        elif index_tuples[info_index][0] == 'Commitment':
                            try:
                                size = int(index_tuples[info_index][1][:-18])
                                if size == 0:
                                    course['Hours/Week'] = None
                                else:
                                    course['Hours/Week'] = size
                            except IndexError:
                                course['Hours/Week'] = index_tuples[info_index][1]    
                        elif index_tuples[info_index][0] == 'Start Date':
                            date = index_tuples[info_index][1]
                            if date != 'Rolling Dates' and date != 'N/A':
                                date = date.replace(' 0', ' ')
                                date_object = datetime.datetime.strptime(date, "%B %d, %Y").date()
                                course[index_tuples[info_index][0]] = str(date_object)
                            else:
                                course[index_tuples[info_index][0]] = date
                        else:
                            course[index_tuples[info_index][0]] = index_tuples[info_index][1]

                        info_index += 1
                except IndexError:
                    pass

                key = name.title()
                courses[key] = course

        item['courses'] = courses
        item['technologies'] = technologies
        item['su_technologies'] = technologies


#=========================================================================================================#
#============================================IN PROGRESS ABOVE============================================#
#=========================================================================================================#   

        for key, value in item.iteritems():
            try:
                temp = str(value)
                if temp == 'No data':
                    item[key] = None
            except ValueError:
                continue
        
        try:
            parsed_hiring_rate = item['hiring_rate'][0][:-1]
            try:
                item['hiring_rate'] = float(parsed_hiring_rate)
            except ValueError:
                pass
        except IndexError:
            pass

        for key, value in item.iteritems():
            if type(value) is list:
                if not value:
                    item[key] = None
                if len(value) == 1:
                    item[key] = value[0]

        if type(item['locations']) == unicode:
            try:
                temp = []
                temp.append(item['locations'])
                item['locations'] = temp
            except TypeError:
                pass

        if item['average_salary'] == 0:
            item['average_salary'] = None

        try:
            num_loc = 0
            for x in item['locations']:
                num_loc += 1
            item['num_locations'] = num_loc
        except TypeError:
            pass

        item['top_source'] = ['SwitchUp']
        item['tracking_groups'] = list()

        today = datetime.date.today()
        item['last_updated'] = str(today)
            
        yield item

#=========================================================================================================#
#***************=============================HELPER FUNCTIONS===============================**************#
#=========================================================================================================#

    def type_converter(self, init_list, new_type):
        if len(init_list) == 0:
            return init_list
        elif len(init_list) == 1:
            try:
                nt = new_type(init_list[0])
                return nt
            except ValueError:
                return init_list[0]
        elif len(init_list) > 1:
            return_list = []
            for x in init_list:
                try:
                    y = new_type(x)
                except ValueError:
                    y = x
                return_list.append(y)
            return return_list

    def find_table_key(self, item, item_dict): 
        front_stub = '//*[@id="bootcamp-summary"]/table/tbody/tr['
        back_stub = ']/td/text()'

        try:
            t_index = item_dict[item]
        except KeyError:
            t_index = 100

        xpath = front_stub + str(t_index) + back_stub

        return xpath

