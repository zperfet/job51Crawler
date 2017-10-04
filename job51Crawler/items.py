# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


# job51中area_code、area_name以及对应的工作数
class Job51AreaItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 区域码
    area_code = Field()
    # 区域名
    area_name = Field()
    # 区域对应的工作数
    # 每次重新爬取工作的时候必须刷新
    area_job_num = Field()
