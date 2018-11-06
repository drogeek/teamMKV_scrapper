import scrapy, re, json, time
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings
from scrapy.shell import inspect_response
from .teamMKV import TeamMKV

class Allocine(scrapy.Spider):
    name = 'allocine'
    # custom_settings={
        # 'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        # 'FEED_FORMAT': 'json',
        # 'FEED_URI': 'teamMKV_films.json'
    # }

    def start_requests(self):
        with open('teamMKV_films.json') as f:
            for index, movie in enumerate(json.load(f)[0]['data']):
                yield scrapy.Request(url='http://www.allocine.fr/recherche/?q='+movie[0], meta={'index':index,'title': movie[0], 'year':movie[1], 'filename':movie[2]})

    def parse(self, response):
        table_1 = response.xpath('//table')[0]
        movies = table_1.xpath('.//tr[td/div/div/span]')
        for m in movies.extract():
            selector = Selector(text=m)
            for span in selector.xpath('.//span'):
                if span.extract().split()[2].startswith(response.meta['year']):
                    yield response.follow(selector.xpath('.//a/@href').extract_first(), callback=self.parse_main, meta=response.meta)
        print('BEWARE: {} was ignored'.format(response.meta['title']))


    def parse_main(self, response):
        item_cont=response.xpath('//div[@class="rating-item-content"]')
        time.sleep(3)
        result = { k:response.meta[k] for k in response.meta if k in ('title','year','index','filename')}
        if item_cont[0].xpath('span/text()').extract_first() == ' Presse ':
            result['score']=item_cont[0].xpath('.//span[@class="stareval-note"]/text()').extract_first().strip()
            yield result 
        else:
            result['score']='unknown'
            yield result 
