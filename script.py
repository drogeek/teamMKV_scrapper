import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from teamMKV import TeamMKV

configure_logging()
runner = CrawlerRunner({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_URI': 'testDeMerde.txt',
    'ROBOTSTXT_OBEY': 'False'
})

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(TeamMKV)
    reactor.stop()
crawl()
reactor.run()
