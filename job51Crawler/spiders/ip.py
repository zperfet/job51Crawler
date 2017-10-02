# -*- coding: utf-8 -*-
import scrapy


# 检测当前IP
class IpSpider(scrapy.Spider):
    name = "ip"
    allowed_domains = ["ip.filefab.com"]
    start_urls = ['http://ip.filefab.com/index.php/']

    def parse(self, response):
        ip = response.selector.xpath('//*[@id="ipd"]/span/text()').extract_first()
        print('ip', ip)
