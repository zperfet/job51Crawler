import re
import os

# 存放数据的文件夹地址，方便迁移
data_address = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
# 正常页面包含的工作数（未动态加载）
normal_page_job_num = 30
# 具体工作的模板链接，最后添加上jobid即可
job_base_url = "http://m.51job.com/search/jobdetail.php?jobtype=0&jobid="
# 工作url本地保存地址
job_url_address = os.path.join(data_address, 'job_url')
# jobarea数据保存地址
job_area_address = os.path.join(data_address, 'job_area')
# jobarea起始url，010000（北京）
jobarea_start_url = 'http://m.51job.com/search/joblist.php?keyword=+&keywordtype=2&funtype=0000&indtype=32&jobarea=010000&jobterm=99&cotype=99&issuedate=9&saltype=99&degree=99&landmark=0&workyear=99&cosize=99&radius=-1&lonlat=0%2C0&pageno=1'
# large_area中的工作数上限，等于上限则需要分区请求
large_area_job_num_ceiling = 100000


# 依据网页链接获取Ajax动态添加的json数据的url
# 输入：当前网页的url
# 返回：网页动态加载对应的json数据的链接列表
def get_ajax_url(url):
    base_page_no = get_page_no(url)
    if base_page_no == 1:
        url += "&pageno=1"
    ajax_urls = [re.sub('pageno=\d+', "pageno=%d" % i, url) for i in range(base_page_no + 1, base_page_no + 10)]
    ajax_urls = [url.replace(".com/search/joblist.php", ".com/ajax/search/joblist.ajax.php") for url in ajax_urls]
    return ajax_urls


# 获取网页url中的pageno
# 输入：当前页面的url
# 返回：当前页面的额pageno
def get_page_no(url):
    try:
        base_page_no = int(re.search('pageno=(\d+)', url).group(1))
    except AttributeError:
        # pageno=1时默认被省略
        base_page_no = 1
    return base_page_no


# 获取下一网页的url
# 输入：当前页面的url
# 返回：下一页面的url
def get_next_page_url(url):
    cur_page_no = get_page_no(url)
    if cur_page_no == 1:
        url += "&pageno=1"
    next_page_no = str(int(cur_page_no) + 10)
    next_page_url = re.sub('pageno=\d+', 'pageno=%s' % next_page_no, url)
    return next_page_url


# 由当前area_code获取下一个area_code,针对大的区域，即修改前2个数字
# 输入：当前area_code,如010000
# 输出：下一个area_code，如020000
def next_large_area_code(area_code):
    next_area_code = str(int(area_code) + 10000)
    if len(next_area_code) == 5:
        next_area_code = '0' + next_area_code
    return next_area_code


# 由大区域area_code得到首个小区域area_code
# 输入：大区域area_code
# 输出：小区域area_code
def small_area_begin_code(area_code):
    if int(area_code) % 10000:
        print('error area code', area_code)
        raise ValueError("传递的large_area_code不正确，后4位应该都为0")
    # 广东省的第一个小区域不是030100而是030200，应该是网站失误
    if area_code[0:2] == '03':
        begin_area_code = area_code[0:2] + '02' + area_code[4:6]
    else:
        begin_area_code = area_code[0:2] + '01' + area_code[4:6]
    return begin_area_code


# 由当前area_code获取下一个area_code,针对大的区域，即修改前2个数字
# 输入：当前area_code,如010000
# 输出：下一个area_code，如020000
def next_small_area_code(area_code):
    next_area_code = str(int(area_code) + 100)
    if len(next_area_code) == 5:
        next_area_code = '0' + next_area_code
    return next_area_code


# 利用area的job数量得到job占据的页面数
# 输入：某area的job数量
# 输出：job占据的页面数
def get_pageno_from_job_num(job_num):
    pageno = int(job_num / 300) * 10 + 1
    return pageno
