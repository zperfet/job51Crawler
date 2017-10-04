# -*- coding: utf-8 -*-
import logging
from scrapy import Spider, Request
from crawlerSpecial.job51_special import *
from job51Crawler.settings import *


# 爬取job51不同区域的工作的链接
class Job51UrlSpider(Spider):
    name = 'job51_url'
    allowed_domains = ['www.51job.com/']
    failed_url = dict()

    def start_requests(self):
        # 加载区域码和工作数
        code_num_dict = load_area_code_and_job_num()
        # 构造start_urls
        for code in code_num_dict.keys():
            job_num = code_num_dict[code]
            approximate_page_num = approximate_pageno_from_job_num(job_num)
            # 只使用以1结尾的pageno发送请求（网站特点）
            # 通过动态加载可以加载剩余9页的数据
            for pageno in range(1, approximate_page_num, 10):
                url = construct_url_upon_code_and_pageno(code, pageno)
                yield Request(url,
                              callback=self.parse,
                              errback=self.error_parse,
                              dont_filter=True,
                              meta={'origin_callback': self.parse},
                              )

                # 对url的ajax数据发送请求
                ajax_urls = get_ajax_url_from_start_url(url)
                for url in ajax_urls:
                    yield Request(url,
                                  callback=self.parse_ajax,
                                  errback=self.error_parse,
                                  dont_filter=True,
                                  meta={'origin_callback': self.parse_ajax},
                                  )

    # 对普通页面的job的url进行收集
    def parse(self, response):
        pass

    # 解析动态加载的ajax数据中的job_url
    def parse_ajax(self):
        pass

    # 解析错误处理
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
