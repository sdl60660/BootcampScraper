# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from scrapy import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import HtmlResponse, Response
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.linkextractors import LinkExtractor

from bootcamp_info.items import SwitchupSchool

class SwitchupSpider(scrapy.Spider):
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
        item['cost'] = Selector(response).xpath('//*[@id="bootcamp-summary"]/table/tbody/tr/td[@itemprop="priceRange"]/text()').extract() #DONE

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

        if not isinstance(item['locations'], list):
            try:
                list(item['locations'])
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

        item['sources'] = ['SwitchUp']
        item['tracking_groups'] = list()
            
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

