# -*- coding: utf-8 -*-
import scrapy


class Job51Spider(scrapy.Spider):
    name = 'job51'
    allowed_domains = ['http://www.51job.com/']
    start_urls = ['http://http://www.51job.com//']

    def parse(self, response):
        pass
