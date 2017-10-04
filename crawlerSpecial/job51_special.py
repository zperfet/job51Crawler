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
area_job_num_ceiling = 100000


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


# 由大区域area_code得到首个中区域area_code
# 输入：大区域area_code
# 输出：中区域area_code
def middle_area_begin_code(area_code):
    if int(area_code) % 10000:
        print('error area code', area_code)
        raise ValueError("传递的large_area_code不正确，后4位应该都为0")
    # 广东省的第一个小区域不是030100而是030200，应该是网站失误
    if area_code[0:2] == '03':
        begin_area_code = area_code[0:2] + '02' + area_code[4:6]
    else:
        begin_area_code = area_code[0:2] + '01' + area_code[4:6]
    return begin_area_code


# 由中区域area_code得到首个小区域area_code
# 输入：中区域area_code
# 输出：小区域area_code
def small_area_begin_code(area_code):
    if int(area_code) % 100:
        print('error area code', area_code)
        raise ValueError("传递的middle_area_code不正确，后2位应该都为0")
    begin_area_code = area_code[0:4] + '01'
    return begin_area_code


# 由当前area_code获取下一个area_code,针对大区域，即修改1-2二个数字
# 输入：当前area_code,如010000
# 输出：下一个area_code，如020000
def next_large_area_code(area_code):
    next_area_code = str(int(area_code) + 10000)
    if len(next_area_code) == 5:
        next_area_code = '0' + next_area_code
    return next_area_code


# 由当前area_code获取下一个area_code,针对中区域，即修改3-4二个数字
# 输入：当前area_code,如010500
# 输出：下一个area_code，如010600
def next_middle_area_code(area_code):
    next_area_code = str(int(area_code) + 100)
    if len(next_area_code) == 5:
        next_area_code = '0' + next_area_code
    return next_area_code


# 由当前area_code获取下一个area_code,针对小的区域，即修改5-6二个数字
# 输入：当前area_code,如010503
# 输出：下一个area_code，如010504
def next_small_area_code(area_code):
    next_area_code = str(int(area_code) + 1)
    if len(next_area_code) == 5:
        next_area_code = '0' + next_area_code
    return next_area_code


# 利用area的job数量得到的大致的页面数，以1结尾，如121
# 最后页面数（如121）构造成的url的页面通过动态加载可以包括所有剩下的数据
# 输入：某area的job数量
# 输出：job占据的页面数
def approximate_pageno_from_job_num(job_num):
    pageno = int(job_num / 300) * 10 + 1
    return pageno


# 依据url获取Ajax动态添加的json数据的url
# 输入：某一url(pageno以1结尾的网页)
# 返回：网页动态加载对应的json数据的链接列表(pageno结尾从2到10)
def get_ajax_url_from_start_url(url):
    base_page_no = get_page_no(url)
    if base_page_no == 1:
        url += "&pageno=1"
    ajax_urls = [re.sub('pageno=\d+', "pageno=%d" % i, url) for i in range(base_page_no + 1, base_page_no + 10)]
    ajax_urls = [url.replace(".com/search/joblist.php", ".com/ajax/search/joblist.ajax.php") for url in ajax_urls]
    return ajax_urls


# 基于area_code获取start_urls
# 输入：area_code
# 输出：不同区域的start_urls
# def get_start_urls_from_area_code():
#     start_urls = list()
#     加载区域码和工作数
    # code_num_dict = load_area_code_and_job_num()
    # 构造start_urls
    # for code in code_num_dict.keys():
    #     job_num = code_num_dict[code]
    #     approximate_page_num = approximate_pageno_from_job_num(job_num)
    #     只使用以1结尾的pageno发送请求（网站特点）
    #     通过动态加载可以加载剩余9页的数据
        # for pageno in range(1, approximate_page_num, 10):
        #     start_url = construct_url_upon_code_and_pageno(code, pageno)
        #     start_urls.append(start_url)
    # return start_urls


# 从本地加载area_code和job_num
# 输入：无
# 输出：area_code：job_num字典
# 数据库准备好后直接从数据库加载
def load_area_code_and_job_num():
    with open(job_area_address, 'r')as f:
        area_code_and_num = [(line.split()[0], line.split()[2]) for line in f.readlines()]
    area_code_and_num_dict = dict()
    # 以code为键，，num为值组建字典
    for item in area_code_and_num:
        area_code_and_num_dict[item[0]] = int(item[1])
    return area_code_and_num_dict


# 基于code和pageno构造url
# 输入：区域code和页数
def construct_url_upon_code_and_pageno(code, pageno):
    url_change_code = re.sub('jobarea=\d+', 'jobarea=%s' % code, jobarea_start_url)
    target_url = re.sub('pageno=\d+', 'pageno=%d' % pageno, url_change_code)
    return target_url
