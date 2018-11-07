import scrapy, re, json, time
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings
from scrapy.shell import inspect_response
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags
import pandas as pd

NEW_MOVIES_FILE='new_movies.json'
TEAMMKV_OUTPUT_FILE='teamMKV_movies.json'

class Movie_Score(scrapy.Item):
    index=scrapy.Field()
    title=scrapy.Field()
    year=scrapy.Field()
    lang=scrapy.Field()
    sub=scrapy.Field()
    score=scrapy.Field()

class Allocine(scrapy.Spider):
    name = 'allocine'
    custom_settings={
         'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
         'FEED_FORMAT': 'json',
         'FEED_URI': 'test2.json',
         'DOWNLOAD_DELAY': 3
    }

    def start_requests(self):
        movies = pd.read_json(TEAMMKV_OUTPUT_FILE)
        with open(NEW_MOVIES_FILE) as f:
            for index, title in json.load(f).items():
                print(index,title)
                movie_info = movies[movies['index'] == int(index)]
                yield scrapy.Request(url='http://www.allocine.fr/recherche/?q='+title, meta={'index':index,'title': title, 'year': str(movie_info['year'].iloc[0]) })

    def parse(self, response):
        table_1 = response.xpath('//table')[0]
        movies = table_1.xpath('.//tr[td/div/div/span]')
        for m in movies.extract():
            selector = Selector(text=m)
            for span in selector.xpath('.//span'):
                if remove_tags(span.extract().split()[2]).startswith(response.meta['year']):
                    yield response.follow(selector.xpath('.//a/@href').extract_first(), callback=self.parse_main, meta=response.meta)


    def parse_main(self, response):
        item_cont=response.xpath('//div[@class="rating-item-content"]')
        result = { k:response.meta[k] for k in response.meta if k in ('title','year','index')}
        if item_cont[0].xpath('span/text()').extract_first().strip() == 'Presse':
            result['score']=item_cont[0].xpath('.//span[@class="stareval-note"]/text()').extract_first().strip()
            yield result 
        else:
            result['score']='unknown'
            yield result 
