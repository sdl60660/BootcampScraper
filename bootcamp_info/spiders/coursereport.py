# -*- coding: utf-8 -*-
import scrapy

from scrapy import Spider
from scrapy.selector import Selector
from scrapy.http import HtmlResponse, Response

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
#from scrapy.spiders import Spider
#from scrapy.selector import Selector

from bootcamp_info.items import CourseReportSchool


class CourseReportSpider(scrapy.Spider):
    name = "coursereport"
    allowed_domains = ["coursereport.com", "facebook.com", "twitter.com"]
    start_urls = (
        'https://www.coursereport.com/schools?page=1',
    )

    def parse(self, response):
        page_url = 'https://www.coursereport.com/schools?page=1'
        yield scrapy.Request(page_url, callback=self.parse_schools)

    def parse_schools(self, response):
        
        empty_check = Selector(response).xpath('//*[@id="schools"]/div[@class="no-schools"]').extract()

        if not empty_check:
            index_count = 0
            schools = Selector(response).xpath('//*[@id="schools"]/li')

            for school in schools:
                url_stub = school.xpath('//div[1]/h3/a/@href').extract()[index_count]
                school_url = 'https://www.coursereport.com/' + url_stub
                index_count += 1
                yield scrapy.Request(school_url, callback=self.parse_contents)

            next_page = Selector(response).xpath('//*[@id="main-content"]/nav[@class="pagination"]/span[@class="next"]/a/@href').extract()
            #if next_page:
            url_stub = str(next_page)[3:-2]
            page_url = 'https://www.coursereport.com' + url_stub
            print
            print
            print "PAGE URL: " + str(page_url)
            print
            print
            yield scrapy.Request(page_url, self.parse_schools)
        else:
            print
            print "*****=====================================================*****"
            print "         HAVE HIT A PAGE THAT'S EMPTY. NOW EXITING..."
            print "*****=====================================================*****"
            print


    def parse_contents(self, response):
        item = CourseReportSchool()

        item['name'] = str(Selector(response).xpath('//*[@id="main-content"]/div[1]/h1/text()').extract())[3:-2].title()
        item['locations'] = Selector(response).xpath('//*[@id="details-collapse"]/div/ul/li[2]/a/text()').extract()
        item['tracks'] = Selector(response).xpath('//*[@id="details-collapse"]/div/ul/li[1]/a/text()').extract()
        item['job_guarantee'] = Selector(response).xpath('//*[@id="more-info-collapse"]/div/p[1]/text()').extract()
        item['job_assistance'] = Selector(response).xpath('//*[@id="more-info-collapse"]/div/p[2]/text()').extract()
        item['accreditation'] = Selector(response).xpath('//*[@id="more-info-collapse"]/div/p[3]/text()').extract()
        #HOUSING PARSE NEEDS TO ACCOUNT FOR THE LINKS THAT DESIGNATE PARTNERSHIPS
        housing_parse = Selector(response).xpath('//*[@id="more-info-collapse"]/div/div/text()').extract()
        if len(housing_parse) > 0:
            item['housing'] = [housing_parse[0]]
        else:
            item['housing'] = housing_parse
        item['visas'] = Selector(response).xpath('//*[@id="more-info-collapse"]/div/p[4]/text()').extract()

        try:
            item['cr_rating'] = float(Selector(response).xpath('//*[@id="main-content"]/div[1]/div/p[2]/span[@class="rating-value"]/text()').extract()[0])
        except IndexError:
            item['cr_rating'] = None
        
        try:
            item['cr_num_reviews'] = int(Selector(response).xpath('//*[@id="main-content"]/div[1]/div/p[2]/span[@itemprop="reviewCount"]/text()').extract()[0])
        except IndexError:
            item['cr_num_reviews'] = None

        try:
            item['website'] = Selector(response).xpath('//*[@id="details-collapse"]/div/ul/li[@class="url"]/a/@href').extract()[0]
        except IndexError:
            item['website'] = None

        try:
            temp_email = str(Selector(response).xpath('//*[@id="details-collapse"]/div/ul/li[@class="email"]/a/@href').extract()[0])
            item['email'] = str(temp_email)[7:]
        except IndexError:
            item['email'] = None

        
        #In course title vs. in course description (gives clues to whether it's a focus on their course or a smaller unit)
        #key_technologies_list = ['Python', 'Java ', '.NET', 'Node', 'Angular', 'JQuery', 'SQL', 'Entity', 'Ruby', 'Django', 'HTML', 'Javascript', 'C#', 'C++', 'CSS', 'Bootstrap', 'Swift', 'Rails', 'Objective-C']

        if len(Selector(response).xpath('//*[@class="campus panel panel-cr"]').extract()) > 0:
            #dict of course title (key) to course information (value)
            courses = {}
            technologies = []

            #dict of location (key) to offered courses (value)
            location_courses = {}

            xpath_id_list = []
            for loc in Selector(response).xpath('//*[@class="col-lg-8 col-xs-12"]/h2/text()').extract():
                loc = loc.lower()
                loc = loc.split(' ')
                loc = ''.join(loc)
                xpath_id_list.append(loc)

            for x, location_id in enumerate(xpath_id_list):
                campus_location = Selector(response).xpath('//*[@class="col-lg-8 col-xs-12"]/h2/text()').extract()[x]
                location_course_list = []

                xpath_front_stub = '//*[@id="'
                xpath_middle = str(location_id)
                xpath_back_stub = '"]//*[@id="courses"]'

                course_array_xpath = xpath_front_stub + xpath_middle + xpath_back_stub

                for y, current_course in enumerate(Selector(response).xpath(course_array_xpath).extract()):
                    course = {}

                    title_xpath = course_array_xpath + '//*[@id="course-listing"]//h4/text()'
                    title = Selector(response).xpath(title_xpath).extract()[y]
                    course['title'] = title

                    course['location'] = campus_location

                    cost_xpath = course_array_xpath + '//*[@class="price"]/span/text()'
                    cost = Selector(response).xpath(cost_xpath).extract()
                    try:
                        course['cost'] = cost[y]
                    except IndexError:
                        course['cost'] = None
                    
                    topic_xpath = course_array_xpath + '[' + str(y + 1) + ']//*[@class="focus"]/a/text()'
                    topics = Selector(response).xpath(topic_xpath).extract()
                    for topic in topics:
                        if topic not in technologies:
                            technologies.append(topic)
                    course['topics'] = topics

                    type_xpath = course_array_xpath + '//*[@class="type"]/text()'
                    onsite_index = y*2
                    partfull_index = (y*2) + 1
                    
                    try:
                        course['onsite'] = Selector(response).xpath(type_xpath).extract()[onsite_index]
                    except IndexError:
                        course['onsite'] = None

                    try:
                        course['part_or_full'] = Selector(response).xpath(type_xpath).extract()[partfull_index]
                    except IndexError:
                        course['onsite'] = None

                    check = course_array_xpath + '//*[@id="newyorkcity"]//*[@id="courses"]//*[@class="dl-horizontal"]/dt/text()'
                    try:
                        if Selector(response).xpath(check).extract()[3] == 'Minimum Skill Level':
                            skill_xpath = course_array_xpath + '//*[@class="dl-horizontal"]/dd/text()'
                            course['min_skill'] = Selector(response).xpath(skill_xpath).extract()[(3 + 5*y)]
                        else:
                            course['min_skill'] = None
                    except IndexError:
                        course['min_skill'] = None
                    
                    try:
                        time_xpath = course_array_xpath + '//*[@class="hours-week-number"]/text()'
                        course['weekly_time'] = Selector(response).xpath(time_xpath).extract()[y]
                    except IndexError:
                        course['weekly_time'] = None

                    #course['about'] = 
                    courses[title] = course
                    location_course_list.append(title)
                
                location_courses[campus_location] = location_course_list

            item['courses'] = courses
            item['technologies'] = technologies
        
        if len(Selector(response).xpath('//*[@id="about-collapse"]/div/section/div[@class="outcomes-title"]/h2/text()').extract()) > 0:
            employment_stats = {}
            employment_stats['30 days'] = int(Selector(response).xpath('//*[@class="thirty-days"]/h3/text()').extract()[0][:-1])
            employment_stats['60 days'] = int(Selector(response).xpath('//*[@class="sixty-days"]/h3/text()').extract()[0][:-1])
            employment_stats['90 days'] = int(Selector(response).xpath('//*[@class="ninety-days"]/h3/text()').extract()[0][:-1])
            employment_stats['120 days'] = int(Selector(response).xpath('//*[@class="one-twenty-days"]/h3/text()').extract()[0][:-1])
            employment_stats['120+'] = int(Selector(response).xpath('//*[@class="over-one-twenty-days"]/h3/text()').extract()[0][:-1])
            item['employment_rates'] = employment_stats

            matriculation_info = {}
            matriculation_info['accepted'] = int(Selector(response).xpath('//*[@class="total-accepted"]/h3/text()').extract()[0])
            matriculation_info['enrolled'] = int(Selector(response).xpath('//*[@class="total-enrolled"]/h3/text()').extract()[0])
            matriculation_info['graduated'] = int(Selector(response).xpath('//*[@class="total-graduated"]/h3/text()').extract()[0])
            matriculation_info['job_seeking'] = int(Selector(response).xpath('//*[@class="total-job-seeking"]/h3/text()').extract()[0])
            item['matriculation_stats'] = matriculation_info

            item['acceptance_rate'] = int(Selector(response).xpath('//*[@class="about"]//p/strong/text()').extract()[0][:-1])
            if len(Selector(response).xpath('//*[@class="about"]//p/strong/text()').extract()[-1]) >= 5:
                item['average_salary'] = Selector(response).xpath('//*[@class="about"]//p/strong/text()').extract()[-1]

        if len(Selector(response).xpath('//*[@class="scholarships"]/h4/text()').extract()) > 0:
            item['scholarships'] = Selector(response).xpath('//*[@class="scholarships"]//*[@class="row"]//h2/text()').extract()

        #=========================================================================================================#
        #============================================IN PROGRESS BELOW============================================#
        #=========================================================================================================#

        
        try:
            fb_url = str(Selector(response).xpath('//*[@class="facebook"]//@href').extract()[0])
            request = scrapy.Request(fb_url, callback=self.facebook_reporter, meta={'item': item}) #meta={'facebook':item}
            yield request
        except IndexError:
            pass
        
        try:
            twitter_url = str(Selector(response).xpath('//*[@class="twitter"]//@href').extract()[0])
            request = scrapy.Request(twitter_url, callback=self.twitter_reporter, meta={'item': item})
            yield request
        except IndexError:
            pass        

        #item['linkedin'] =

        #=========================================================================================================#
        #============================================IN PROGRESS ABOVE============================================#
        #=========================================================================================================#

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

        item['num_locations'] = len(item['locations'])
        item['num_courses'] = len(item['courses'])
        
        item['sources'] = []
        item['tracking_groups'] = []

        #item['about'] =  
        #item['reviews'] = 

        yield item

    def panel_xpath_helper(self, index, stub):
        xpath_start = '//*[@id="courses-collapse"]/div[@class="panel-body"]/section[@class="campuses"]/div[@class="campus panel panel-cr"]['
        xpath_index = index + 1
        xpath = xpath_start + str(xpath_index) + ']' + stub
        #print
        #print "XPATH: " + str(xpath)
        #print
        return xpath

    def class_xpath_helper(self, index, c_index, stub):
        xpath_index = c_index + 1
        xpath_start = self.panel_xpath_helper(index, '')
        middle = '/div[@class="panel-body accordion"]/div[@class="panel panel-cr panel-cr-expandable"]['
        xpath = xpath_start + middle + str(xpath_index) + ']' + stub
        return xpath


    def facebook_reporter(self, response):
        item = response.meta['item']
        facebook = {}

        #item = response.meta['facebook_item']
        #IF THIS WORKS, THEN CONVERT THESE TO INTS
        print
        print "====================================================="
        full_return = Selector(response).xpath('//*[@class="_52id _50f5 _50f7"]/text()').extract()
        print "Full Return Array: " + str(full_return)
        try:
            likes = Selector(response).xpath('//*[@class="_52id _50f5 _50f7"]/text()').extract()[0]
            #format as an int
            likes = int(''.join((likes[:-1]).split(',')))
            print "Likes: " + str(likes)
            facebook['likes'] = likes
        except IndexError:
            print "ERROR REPORTING. HERE'S THE RETURNED VALUE: " + str(Selector(response).xpath('//*[@class="_52id _50f5 _50f7"]/text()').extract())
        
        try:
            visits = Selector(response).xpath('//*[@class="_52id _50f5 _50f7"]/text()').extract()[1]
            #format as an int
            visits = int(''.join(visits.split(',')))
            print "Visits: " + str(visits)
            facebook['visits'] = visits
        except IndexError:
            facebook['visits'] = None

        print "====================================================="
        print
        
        item['facebook'] = facebook
        return item

    def twitter_reporter(self, response):
        item = response.meta['item']
        twitter = {}

        tweets = Selector(response).xpath('//a[@data-nav="tweets"]//*[@class="ProfileNav-value"]/text()').extract()[0]
        
        try:
            tweets = int(''.join(tweets.split(',')))
        except ValueError:
            if tweets[-1] == 'K':
                tweets = 100*(int(''.join((tweets[:-1]).split('.'))))
            elif tweets[-1] == 'M':
                tweets = 100000*(int(''.join((tweets[:-1]).split('.'))))

            else:
                pass
        twitter['tweets'] = tweets

        followers = Selector(response).xpath('//a[@data-nav="followers"]//*[@class="ProfileNav-value"]/text()').extract()[0]
        try:
            followers = int(''.join(followers.split(',')))
        except ValueError:
            if followers[-1] == 'K':
                followers = 100000*(int(''.join((followers[:-1]).split('.'))))
            elif followers[-1] == 'M':
                followers = 100000*(int(''.join((followers[:-1]).split('.'))))
            else:
                pass

        print 
        print "====================================================="
        print "Twitter Info:"
        print " ----------- "
        print
        print "Followers: " + str(followers)
        print "Tweets: " + str(tweets)
        print "====================================================="
        print

        twitter['followers'] = followers

        item['twitter'] = twitter
        return item






#7. Work with either MongoDB or Postgres to store information in a database
#9. Work on program that will compare tables and track changes
#10.Work on program to automatically compile relevant information into summary email

