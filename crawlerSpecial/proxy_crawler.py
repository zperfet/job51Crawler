import os

# 存放数据的文件夹地址，方便迁移
data_address = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
# 快代理的爬取页数
kuaidaili_page_num = 10
# 代理保存地址
proxies_address = os.path.join(data_address, 'proxies')
