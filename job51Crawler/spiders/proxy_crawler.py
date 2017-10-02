# -*- coding: utf-8 -*-
from crawlerSpecial.proxy_crawler import *
import json
from scrapy.http import Request
from scrapy import Spider


class ProxyCrawlerSpider(Spider):
    name = "proxy"
    allowed_domains = ["www.kuaidaili.com"]
    kuaidaili_page_num = kuaidaili_page_num
    start_urls = ['http://www.kuaidaili.com/free/inha/%d/' %
                  i for i in range(1, kuaidaili_page_num + 1)]
    proxies_lst = list()

    def parse(self, response):
        ip = response.selector.xpath('//td[@data-title="IP"]/text()').extract()
        port = response.selector.xpath('//td[@data-title="PORT"]/text()').extract()
        self.proxies_lst += (list(zip(ip, port)))

    def close(self, reason):
        # 将代理保存到本地
        with open(proxies_address, 'w', encoding='utf-8')as f:
            print('将%d个代理保存到本地' % len(self.proxies_lst))
            json.dump(self.proxies_lst, f)

