# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from job51Crawler.settings import *
from job51Crawler.items import *


# 保存不同区域信息的pipeline，包括区域码、区域名、区域工作数
class Job51AreaPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            database=JOB51_DB,
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        if item.__class__ == Job51AreaItem:
            # 调用存储过程将area信息存储到
            print(dict(item).values())
            # todo
            # 测试字典传递数据的顺序是否有问题
            self.cursor.callproc('insert_area', dict(item).values())
        return item
