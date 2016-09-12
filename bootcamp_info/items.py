# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class CourseReportSchool(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    name = Field()
    locations = Field()
    tracks = Field()
    job_guarantee = Field()
    job_assistance = Field()
    accreditation = Field()
    housing = Field()
    visas = Field()

    cr_rating = Field()
    cr_num_reviews = Field()

    website = Field()
    email = Field()

    courses = Field()
    location_courses_dict = Field()
    scholarships = Field()
    acceptance_rate = Field()
    employment_rates = Field() #[30 days, 60 days, 90 days, 120 days, after 120 days]
    matriculation_stats = Field() #[Accepted, Enrolled, Graduated, Job Seeking]
    average_salary = Field()

    technologies = Field()
    cr_technologies = Field()

    facebook = Field()
    twitter = Field()
    linkedin = Field()

    top_source = Field()

    num_locations = Field()
    num_courses = Field()
    tracking_groups = Field()

    last_updated = Field()

    #about = Field()
    #reviews = Field()

class BootcampsInSchool(Item):

    name = Field()
    locations = Field()
    countries = Field()
    primary_city = Field()
    started = Field()
    BCtype = Field()
    focus = Field()

    length = Field()
    class_size = Field()
    time_per_week = Field()
    min_skill_level = Field()
    placement_test = Field()
    prep_work = Field()
    interview = Field()

    cost = Field()
    deposit = Field()
    payments = Field()

    job_assistance = Field()
    housing = Field()
    visas = Field()

    email = Field()
    phone = Field()
    address = Field()
    address_city = Field()
    address_country = Field()

    top_source = Field()

    num_locations = Field()
    tracking_groups = Field()

    last_updated = Field()

    #about = Field()
    #url = Field()
    #logo_image = Field()

class SwitchupSchool(Item):

    name = Field()
    locations = Field()
    general_cost = Field()  #key: $ = < $5,000; $$ = $5,000-10,000; $$$ = $10,000-$14,000; $$$$ = $14,000+

    website = Field()

    scholarships = Field()
    subjects = Field()
    hiring_rate = Field()
    average_salary = Field()
    num_alumni = Field()
    class_ratio = Field()

    su_rating = Field()
    su_num_reviews = Field()

    num_locations = Field()
    tracking_groups = Field()

    courses = Field()
    technologies = Field()
    su_technologies = Field()

    top_source = Field()

    page = Field()

    last_updated = Field()

    #tracks = Field() #figure out a way to get this field to include description, subjects, location, cost, start dates,
    #class size, length and commitment (which are shown on the page)
    #about = Field()
    #reviews = Field()

class AlexaPage(Item):
    name = Field()
    alexa_data = Field()




"""
class BootcampInfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
"""