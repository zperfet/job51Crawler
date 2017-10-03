# -*- coding: utf-8 -*-
from scrapy import Spider


# 爬取job51不同区域的工作的链接
class Job51UrlSpider(Spider):
    name = 'job51_url'
    allowed_domains = ['www.51job.com/']
    start_urls = ['http://www.51job.com//']

    def parse(self, response):
        pass

    # 获取不同区域的工作的起始页面
    def get_start_urls(self):
        pass
