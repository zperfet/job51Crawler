# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy import Request
from crawlerSpecial.job51_special import *
import re


class JobareaSpider(Spider):
    name = "job_area"
    allowed_domains = ["51job.com"]
    start_urls = [jobarea_start_url]
    large_area = dict()
    small_area = dict()

    def parse(self, response):
        area_code = re.search('jobarea=(\d{6})', response.url).group(1)
        area_name = response.selector.xpath('//*[@id="landmark"]/text()').extract()[0][1:]
        if area_name not in self.large_area.values():
            # 保存large_area的name和code
            self.large_area[area_code] = area_name
            # 对下一个large_area发送Request
            next_large_area_url = re.sub('jobarea=\d{6}', 'jobarea=%s' %
                                         next_large_area_code(area_code), response.url)
            yield Request(next_large_area_url, callback=self.parse)

            # 获取每个大区域的工作数
            large_area_job_num = int(response.selector.xpath('//p[@class="result"]/span/text()').extract()[0])
            # large_area工作数字超过数字上限的的需要分区请求
            if large_area_job_num == large_area_job_num_ceiling:
                print("%s需要分区请求（%d）" % (area_name, large_area_job_num))
                small_area_code = small_area_begin_code(area_code)
                small_area_begin_url = re.sub('jobarea=\d{6}', 'jobarea=%s' % small_area_code, response.url)
                yield Request(small_area_begin_url, callback=self.parse_small_area)
            # 工作数字在100000的直接保留large_area的name和code即可
            elif large_area_job_num and large_area_job_num < large_area_job_num_ceiling:
                print("%s不需要需要分区请求（%d）" % (area_name, large_area_job_num))
                # 对应区域的工作数占据的总页数
                area_pageno = get_pageno_from_job_num(large_area_job_num)
                with open(job_area_address, 'a', encoding='utf-8')as f:
                    f.write(area_code + ' ' + area_name + ' ' + str(area_pageno) + '\n')
            else:
                raise ValueError('large_area_job_num数字%s有问题，应该在0~%s之间' %
                                 (large_area_job_num, large_area_job_num_ceiling))

    # 解析更小的区域对应的area_code
    def parse_small_area(self, response):
        area_code = re.search('jobarea=(\d{6})', response.url).group(1)
        small_area_name = response.selector.xpath('//*[@id="landmark"]/text()').extract()[0][1:]
        large_area_name = self.large_area[area_code[0:2] + '0000']
        area_name = large_area_name + small_area_name
        if small_area_name not in self.large_area.values() \
                and area_name not in self.small_area.values():
            self.small_area[area_code] = area_name
            # 获取每个小区域的工作数
            small_area_job_num = int(response.selector.xpath('//p[@class="result"]/span/text()').extract()[0])
            area_pageno = get_pageno_from_job_num(small_area_job_num)
            with open(job_area_address, 'a', encoding='utf-8')as f:
                f.write(area_code + ' ' + area_name + ' ' + str(area_pageno) + '\n')
            print('保存的小区域', area_name, ' ', area_code)
            next_small_area_url = re.sub('jobarea=\d{6}', 'jobarea=%s' %
                                         next_small_area_code(area_code), response.url)
            yield Request(next_small_area_url, callback=self.parse_small_area)
