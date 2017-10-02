from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# execute("scrapy crawl job51".split())
# execute("scrapy crawl job_area".split())
# execute("scrapy crawl proxy".split())
execute("scrapy crawl ip".split())
