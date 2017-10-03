# job51Crawler
Crawler for http://www.51job.com/

目标是爬取51job网站的全部职位用于数据分析。

crawlerSpecial:
和特定爬虫有关的参数和函数，目前是和51job这个网站有关的一些参数和函数

data：
爬取的数据，目前主要是51job网站的“地图”--不同区域的名字、区域码以及一个和工作数有关的数字，具体见代码；

rscData:
资源文件夹，目前只有user-agent;代理存储在数据库，代理的维持项目有空会开源；

job51Crawler:
scrapy生成的主文件夹，各文件的作用见scrapy文档。
ip.py是个测试文件，不用管；
job_area.py基本完成，分区域保存区域码，方便构造不同区域的工作的url。
job_url.py是用于爬取工作url的爬虫，会很快更新；
还有一个用于爬取具体工作的爬虫尚未添加。

Proxy和User-Agent部分暂时不介绍，具体可见代码注释。后期有时间再展开。

更多的细节暂时不讨论，因为可能会再变，后期会陆续添加。有需要可看代码注释，较为详细。

有任何建议或者问题请联系我：zperfet007@gmail.com
