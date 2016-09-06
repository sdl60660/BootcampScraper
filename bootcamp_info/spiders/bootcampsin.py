# -*- coding: utf-8 -*-
import scrapy

import datetime

from scrapy import Spider
from scrapy.selector import Selector
from scrapy.http import HtmlResponse, Response

from bs4 import BeautifulSoup

#from scrapy.spiders import Spider
#from scrapy.selector import Selector

from bootcamp_info.items import BootcampsInSchool


class BootcampsinSpider(scrapy.Spider):
    name = "bootcampsin"
    allowed_domains = ["bootcamps.in"]
    start_urls = (
        'http://www.bootcamps.in/',
    )

    def parse(self, response):
        index_count = 0

        schools = Selector(response).xpath('//*/article/div[1]/a/@href').extract()
        for school in schools:
            url_stub = schools[index_count]
            school_url = 'http://www.bootcamps.in/' + url_stub
            index_count += 1
            yield scrapy.Request(school_url, callback=self.parse_contents)

    def parse_contents(self, response):
        url = response.request.url
        primary_city = (' '.join((url.split('/')[3]).split('-'))).title()

        #'http://www.bootcamps.in/portland/pdx-code-guild/'

        item = BootcampsInSchool()

        item['name'] = str(Selector(response).xpath('//*/header/h1/text()').extract())[3:-2].title()
        item['locations'] = Selector(response).xpath('//*/div[2]/div[1]/a/text()').extract()
        item['countries'] = self.link_xpath_helper(response, 33)
        item['primary_city'] = primary_city
        item['started'] = Selector(response).xpath('//*[@id="compare"]/table/tr[6]/td[2]/text()').extract()
        item['BCtype'] = Selector(response).xpath('//*[@id="compare"]/table/tr[4]/td[2]/text()').extract()
        item['focus'] = Selector(response).xpath('//*[@id="compare"]/table/tr[5]/td[2]/a/text()').extract()

        #'length' is probably worth parsing down to an int
        item['length'] = Selector(response).xpath('//*[@id="compare"]/table/tr[8]/td[2]/a/text()').extract()#probably worth parsing down to an int
        item['class_size'] = Selector(response).xpath('//*[@id="compare"]/table/tr[9]/td[2]/a/text()').extract()
        item['time_per_week'] = Selector(response).xpath('//*[@id="compare"]/table/tr[11]/td[2]/text()').extract()
        item['min_skill_level'] = Selector(response).xpath('//*[@id="compare"]/table/tr[12]/td[2]/a/text()').extract()
        item['placement_test'] = Selector(response).xpath('//*[@id="compare"]/table/tr[13]/td[2]/text()').extract()
        item['prep_work'] = Selector(response).xpath('//*[@id="compare"]/table/tr[14]/td[2]/text()').extract()
        item['interview'] = Selector(response).xpath('//*[@id="compare"]/table/tr[15]/td[2]/text()').extract()
        
        item['cost'] = self.link_xpath_helper(response, 17)
        #item['scholarships'] = Selector(response).xpath('//*[@id="compare"]/table/tr[21]/td[2]/text()').extract()
        item['deposit'] = Selector(response).xpath('//*[@id="compare"]/table/tr[22]/td[2]/text()').extract()
        item['payments'] = Selector(response).xpath('//*[@id="compare"]/table/tr[23]/td[2]/text()').extract()

        item['job_assistance'] = self.link_xpath_helper(response, 25)
        item['housing'] = Selector(response).xpath('//*[@id="compare"]/table/tr[26]/td[2]/text()').extract()
        item['visas'] = Selector(response).xpath('//*[@id="compare"]/table/tr[27]/td[2]/text()').extract()
        
        item['email'] = Selector(response).xpath('//*[@id="compare"]/table/tr[29]/td[2]/text()').extract()
        item['phone'] = Selector(response).xpath('//*[@id="compare"]/table/tr[30]/td[2]/text()').extract()
        item['address'] = Selector(response).xpath('//*[@id="compare"]/table/tr[31]/td[2]/text()').extract()
        item['address_city'] = self.array_parser(self.link_xpath_helper(response, 32))
        item['address_country'] = self.array_parser(self.link_xpath_helper(response, 33))
        
        item = self.item_parsers(item)

        if not isinstance(item['locations'], list):
            if not type(item['locations']) == None:
                list(item['locations'])

        try:
            num_loc = 0
            for x in item['locations']:
                num_loc += 1
            item['num_locations'] = num_loc
        except TypeError:
            pass

        item['top_source'] = ['BootcampsIn']
        item['tracking_groups'] = list()

        today = datetime.date.today()
        item['last_updated'] = str(today)

        yield item


###==================HELPER FUNCTIONS FOR ITEM VALUES AND XPATHS==================###

    #DECIDE WHICH XPATH TO USE FOR A VALUE, WHERE THAT VALUE IS
    #SOMETIMES TEXT AND SOMETIMES A LINK
    def link_xpath_helper(self, response, table_number):
        text_xpath = '//*[@id="compare"]/table/tr[' + str(table_number) + ']/td[2]/text()'
        link_xpath = '//*[@id="compare"]/table/tr[' + str(table_number) + ']/td[2]/a/text()'

        text_option = Selector(response).xpath(text_xpath).extract()
        link_option = Selector(response).xpath(link_xpath).extract()

        if len(text_option) == len(link_option) == 0:
            return text_option
        elif len(text_option) > len(link_option):
            return text_option
        else:
            return link_option

    #MAKE SURE VALUES LIKE LINE BREAKS DON'T GET PROCESSED AS ITEM VALUES
    def array_parser(self, array):
        for item in array:
            if len(str(item)) > 2:
                return item

    #PROCESS ITEM VALUES/CORRECT DATA TYPES
    def item_parsers(self, item):
        for key, value in item.iteritems():
            temp = value
            if type(value) == list:
                temp = ' '.join(value)
                temp = ''.join(temp.splitlines())

            if temp is not None:
                if len(temp) > 0 and temp[0] == '?':
                    temp = None
                elif len(temp) > 2 and temp[0:3] == 'N/A':
                    temp = None
                elif len(temp) > 3 and temp[0:4] == '\r\n':
                    temp = temp[4:]

            item[key] = temp

        for key, value in item.iteritems():
            if type(value) is list:
                if not value:
                    item[key] = None
                if len(value) == 1:
                    item[key] = value[0]

        return item

