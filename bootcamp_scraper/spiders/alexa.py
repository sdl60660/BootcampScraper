#NOTE: DO NOT RUN THIS SPIDER, TURNS OUT (OBVIOUSLY) THAT ALEXA IS NOT A FAN OF WEB SCRAPING BECAUSE
#THEY SELL ACCESS TO THEIR API. YOUR IP WILL GET BANNED FROM ALEXA IF YOU RUN THIS REPEATEDLY. MIGHT BE WORTH
#RUNNING ONE TIME THOUGH JUST TO GET INITIAL INFO.

# -*- coding: utf-8 -*-
import scrapy
import json
import os, fnmatch
import datetime
from datetime import date

from bootcamp_scraper.items import AlexaPage

def find_recent_output():
    path = 'old_data/full_outputs/'
    pattern = '*'
    
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result[-1]

class AlexaSpider(scrapy.Spider):
    name = "alexa"
    allowed_domains = ["alexa.com"]
    start_urls = (
        'http://www.alexa.com/siteinfo/',
    )

    def parse(self, response):
        json_data = find_recent_output()
        full_data = open(json_data)
        data = json.load(full_data)

        print
        print "============================"
        print
        for item in data:
            try:
                name = item
                website = data[item]['website']
                page_url = 'http://www.alexa.com/siteinfo/' + str(website)
                yield scrapy.Request(page_url, callback=lambda r, name=name:self.parse_page(r, name))
            except KeyError:
                pass
        print
        print "============================"
        print
        

        #yield scrapy.Request(page_url, callback=self.parse_schools)

    def parse_page(self, response, name):
        item = AlexaPage()
        alexa = {}

        item['name'] = name

        stats_array = Selector(response).xpath('//*[@class="metrics-data align-vmiddle"]/text()').extract()
        alexa['global_rank'] = int(''.join(stats_array[0].split(',')))
        alexa['domestic_rank'] = int(''.join(stats_array[1].split(',')))

        alexa['country'] = Selector(response).xpath('//h4[@class="metrics-title"]/a/text()').extract()[0]

        alexa['bounce_rate'] = stats_array[2]
        alexa['daily_pageviews_per_visitor'] = stats_array[3]
        alexa['daily_time_on_site'] = stats_array[4]
        alexa['search_visits'] = stats_array[5]

        keywords_array = Selector(response).xpath('//*[@id="keywords_top_keywords_table"]/tbody/tr/td/span/text()').extract()
        keywords_data = []
        x = 0
        while x < len(keywords_array):
            keywords_data.append((keywords_array[x+1], keywords_array[x+2]))
            x += 3
        alexa['top_keywords'] = keywords_data 
        num_sites = Selector(response).xpath('//*[@id="linksin-panel-content"]/div/span/div/span/text()').extract()[0]
        alexa['sites_linking_in'] = int(''.join(num_sites.split(',')))

        today = date.today()
        alexa['updated'] = str(today)

        item['alexa_data'] = alexa

        yield item












