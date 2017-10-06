# -*- coding: utf-8 -*-
import scrapy


# 将area_code数据存储到数据库后再添加该爬虫
# 从数据库中读取区域码后在线获取工作数，再更新数据库

# 每次重新爬取工作前需要跟新工作数
class JobNumSpider(scrapy.Spider):
    name = "job_num"
    allowed_domains = ["51job.com"]
    # todo
    start_urls = ['http://']

    def parse(self, response):
        pass
