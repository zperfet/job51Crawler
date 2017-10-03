# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy import Request
from crawlerSpecial.job51_special import *
import re
from job51Crawler.settings import *
import logging


class JobareaSpider(Spider):
    name = "job_area"
    allowed_domains = ["51job.com"]
    start_urls = [jobarea_start_url]
    # 对应area_code1-2位
    large_area = dict()
    # 对应area_code3-4位
    middle_area = dict()
    # 对应area_code5-6位
    small_area = dict()
    # 请求失败的url，主要是因为使用的代理失效导致的
    # 用于记录因为代理失误导致的失败次数
    failed_url = dict()

    # 该函数用于对start_urls发送请求
    # 重载的原因在于添加errback，保证start_urls
    # 也可以切换代理
    def make_requests_from_url(self, url):
        return Request(url,
                       dont_filter=True,
                       callback=self.parse_large_area,
                       errback=self.error_parse,
                       meta={'origin_callback': self.parse_large_area},
                       )

    # 解析大区域对应的area_code,针对area_code前二位
    def parse_large_area(self, response):
        try:
            area_code = re.search('jobarea=(\d{6})', response.url).group(1)
        except Exception as e:
            print('url error result in area_code error', response.url, e)
            return
        try:
            area_name = response.selector.xpath('//*[@id="landmark"]/text()').extract()[0][1:]
        except Exception as e:
            print('area_name error', response.selector.xpath('//*[@id="landmark"]/text()').extract(), e)
            print('获取area_name有误，重新请求')
            yield Request(response.url,
                          callback=self.parse_large_area,
                          errback=self.error_parse,
                          dont_filter=True,
                          meta={'origin_callback': self.parse_large_area},
                          )
            return
        if area_name not in self.large_area.values():
            # 保存large_area的name和code
            self.large_area[area_code] = area_name
            # 对下一个large_area发送Request
            next_large_area_url = re.sub('jobarea=\d{6}', 'jobarea=%s' %
                                         next_large_area_code(area_code), response.url)
            # 重复发送Request的url会被自动删除掉，所以添加了
            # dont_filter=True，使得同一url可以多次切换代理
            yield Request(next_large_area_url,
                          callback=self.parse_large_area,
                          errback=self.error_parse,
                          dont_filter=True,
                          meta={'origin_callback': self.parse_large_area},
                          )
            # 获取每个大区域的工作数
            large_area_job_num = int(response.selector.xpath('//p[@class="result"]/span/text()').extract()[0])
            # large_area工作数字超过数字上限的的需要分区请求
            if large_area_job_num == area_job_num_ceiling:
                print("%s需要分区请求（%d）" % (area_name, large_area_job_num))
                middle_area_code = middle_area_begin_code(area_code)
                middle_area_begin_url = re.sub('jobarea=\d{6}', 'jobarea=%s' % middle_area_code, response.url)
                yield Request(middle_area_begin_url,
                              callback=self.parse_middle_area,
                              errback=self.error_parse,
                              dont_filter=True,
                              meta={'origin_callback': self.parse_middle_area},
                              )
            # 工作数字小于100000的直接保留large_area的name和code即可
            elif 0 < large_area_job_num < area_job_num_ceiling:
                print("%s不需要分区请求（%d）" % (area_name, large_area_job_num))
                # 对应区域的工作数占据的总页数
                area_pageno = get_pageno_from_job_num(large_area_job_num)
                print('保存的大区域', area_name, area_code)
                with open(job_area_address, 'a', encoding='utf-8')as f:
                    f.write(area_code + ' ' + area_name + ' ' + str(area_pageno) + '\n')
            else:
                raise ValueError('large_area_job_num数字%s有问题，应该在0~%s之间' %
                                 (large_area_job_num, area_job_num_ceiling))

    # 解析中等的区域对应的area_code,针对area_code3-4位
    def parse_middle_area(self, response):
        area_code = re.search('jobarea=(\d{6})', response.url).group(1)
        try:
            middle_area_name = response.selector.xpath('//*[@id="landmark"]/text()').extract()[0][1:]
        except Exception as e:
            print(response.url)
            print('area_name error', response.selector.xpath('//*[@id="landmark"]/text()').extract(), e)
            print('获取area_name有误，重新请求')
            yield Request(response.url,
                          callback=self.parse_middle_area,
                          errback=self.error_parse,
                          dont_filter=True,
                          meta={'origin_callback': self.parse_middle_area},
                          )
            return
        large_area_name = self.large_area[area_code[0:2] + '0000']
        area_name = large_area_name + middle_area_name
        # 如果中区域area_code的最后一个有效code是030800
        # 那么下一个code030900形成的url则是对应大区域的url
        if middle_area_name not in self.large_area.values() \
                and area_name not in self.middle_area.values():
            self.middle_area[area_code] = area_name
            # 对下一个中等区域发起请求
            next_middle_area_url = re.sub('jobarea=\d{6}', 'jobarea=%s' %
                                          next_middle_area_code(area_code), response.url)
            yield Request(url=next_middle_area_url,
                          callback=self.parse_middle_area,
                          errback=self.error_parse,
                          dont_filter=True,
                          meta={'origin_callback': self.parse_middle_area},
                          )
            # 获取每个中等区域的工作数
            middle_area_job_num = int(response.selector.xpath('//p[@class="result"]/span/text()').extract()[0])
            # 中等区域超过100000需要再次分区请求
            if middle_area_job_num == area_job_num_ceiling:
                print("%s需要分区请求（%d）" % (area_name, middle_area_job_num))
                small_area_code = small_area_begin_code(area_code)
                small_area_begin_url = re.sub('jobarea=\d{6}', 'jobarea=%s' % small_area_code, response.url)
                yield Request(small_area_begin_url,
                              callback=self.parse_small_area,
                              errback=self.error_parse,
                              dont_filter=True,
                              meta={'origin_callback': self.parse_small_area},
                              )
            elif 0 < middle_area_job_num < area_job_num_ceiling:
                print("%s不需要分区请求（%d）" % (area_name, middle_area_job_num))
                print('保存的中区域', area_name, area_code)
                # 对应区域的工作数占据的总页数
                area_pageno = get_pageno_from_job_num(middle_area_job_num)
                with open(job_area_address, 'a', encoding='utf-8')as f:
                    f.write(area_code + ' ' + area_name + ' ' + str(area_pageno) + '\n')
            else:
                raise ValueError('middle_area_job_num数字%s有问题，应该在0~%s之间' %
                                 (middle_area_job_num, area_job_num_ceiling))

    # 解析小的区域对应的area_code,针对area_code5-6位
    def parse_small_area(self, response):
        area_code = re.search('jobarea=(\d{6})', response.url).group(1)
        small_area_name = response.selector.xpath('//*[@id="landmark"]/text()').extract()[0][1:]
        middle_area_name = self.middle_area[area_code[0:4] + '00']
        area_name = middle_area_name + small_area_name
        # 如果小区域area_code的最后一个有效code是030211
        # 那么下一个code030212形成的url则是对应中等区域的url
        if small_area_name not in self.middle_area.values() \
                and small_area_name not in self.large_area.values() \
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
            yield Request(url=next_small_area_url,
                          callback=self.parse_small_area,
                          errback=self.error_parse,
                          dont_filter=True,
                          meta={'origin_callback': self.parse_small_area},
                          )

    # 大区域解析错误处理
    def error_parse(self, failure):
        # 报告错误
        self.logger.error(repr(failure))
        request = failure.request
        url = request.url
        # 判断url是否已重新发送过
        if url in self.failed_url.keys():
            # 如果url未超过失败次数上限，则重新发送请求（代理不同）
            if self.failed_url[url] < FAIL_TOLERATE_PER_URL:
                self.failed_url[url] += 1
                # 重新发送请求，因为可能是代理问题，重新发送后代理已经切换
                yield Request(url,
                              # callback=self.parse,
                              callback=request.meta['origin_callback'],
                              errback=self.error_parse,
                              dont_filter=True,
                              meta={'origin_callback': request.meta['origin_callback']},
                              )
            else:
                print('%s无法访问，已切换%d次代理'
                      % (url, FAIL_TOLERATE_PER_URL))
                logging.error(msg='%s无法访问，已切换%d次代理'
                                  % (url, FAIL_TOLERATE_PER_URL))
        else:
            # 首次出错，添加到出错url中
            self.failed_url[url] = 1
            # 重新发送请求，因为可能是代理问题，重新发送后代理已经切换
            yield Request(url,
                          callback=request.meta['origin_callback'],
                          errback=self.error_parse,
                          dont_filter=True,
                          meta={'origin_callback': request.meta['origin_callback']},
                          )
