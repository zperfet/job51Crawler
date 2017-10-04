# -*- coding: utf-8 -*-
import scrapy


# 每次重新爬取工作前需要跟新工作数
class JobNumSpider(scrapy.Spider):
    name = "job_num"
    allowed_domains = ["51job.com"]
    # todo
    start_urls = ['http://']

    def parse(self, response):
        pass
