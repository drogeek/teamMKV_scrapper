import scrapy, re

class TeamMKV(scrapy.Spider):
    name = 'teamMKV'
    start_urls = ['http://xdcclist.us.to/?team=Team-MKV&xdcc_id=1']

    def parse(self, response):
#        for title in response.xpath('//b/a/@title').extract(): 
        yield { 'data' : [ (' '.join(re.match('(.*)([0-9]{4})',x).group(1).split('.')),re.match('(.*)([0-9]{4})',x).group(2),x) for x in response.xpath('//b/a/@title').extract() ] }
