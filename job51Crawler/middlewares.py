# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
import logging
import pymysql
import base64
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from rscData.user_agent import USER_AGENT
from job51Crawler.settings import *


class Job51CrawlerSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# user-agent中间件，为每个request随机设置一个user-agent
class RandomUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        super().__init__()
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = random.choice(USER_AGENT)
        if ua:
            request.headers['User-Agent'] = ua
            logging.debug(msg='User-Agent:%s' % ua)


class RandomProxyMiddleware(object):
    log = logging.getLogger('scrapy.proxies')

    def __init__(self, settings):
        self.connect = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            database=PROXY_DB,
        )
        self.cursor = self.connect.cursor()
        self.cursor.callproc('get_valid_proxy')
        self.total_proxies = ['http://' + item[0] + ':' + item[1] for item in
                              self.cursor.fetchall()]
        self.proxies = {}
        for proxy in self.total_proxies:
            self.proxies[proxy] = ''
            # self.proxy_list = settings.get('PROXY_LIST')
            # if self.proxy_list is None:
            #     raise KeyError('PROXY_LIST setting is missing')

            # fin = open(self.proxy_list)

            # self.proxies = {}
            # for line in fin.readlines():
            #     parts = re.match('(\w+://)(\w+:\w+@)?(.+)', line.strip())
            #     if not parts:
            #         continue

            # Cut trailing @
            # if parts.group(2):
            #     user_pass = parts.group(2)[:-1]
            # else:
            #     user_pass = ''

            # self.proxies[parts.group(1) + parts.group(3)] = user_pass

            # fin.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Don't overwrite with a random one (server-side state for IP)
        if 'proxy' in request.meta:
            return

        if len(self.proxies) == 0:
            raise ValueError('All proxies are unusable, cannot proceed')

        proxy_address = random.choice(list(self.proxies.keys()))
        proxy_user_pass = self.proxies[proxy_address]

        request.meta['proxy'] = proxy_address
        if proxy_user_pass:
            basic_auth = 'Basic ' + base64.encodebytes(proxy_user_pass)
            request.headers['Proxy-Authorization'] = basic_auth
        self.log.debug('Using proxy <%s> for %s, %d valid proxies left' % (
            proxy_address, request.url, len(self.proxies)))
        print('Using proxy <%s>, %d valid proxies left' % (
            proxy_address, len(self.proxies)))

    def process_exception(self, request, exception, spider):
        if 'proxy' not in request.meta:
            return

        proxy = request.meta['proxy']
        retry_times = request.meta.get('retry_times', 0)
        if retry_times >= RETRY_TIMES:
            try:
                del self.proxies[proxy]
                self.log.info('Removing failed proxy <%s>, %d valid proxies left' % (
                    proxy, len(self.proxies)))
            except KeyError:
                pass


    def close_spider(self):
        print('end middlewares')
