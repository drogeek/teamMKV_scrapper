import scrapy, re, json, time
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings
from scrapy.shell import inspect_response
from w3lib.html import remove_tags

NEW_MOVIES_FILE='new_movies.json'
TEAMMKV_OUTPUT_FILE='teamMKV_movies.json'

class Movie_Score(scrapy.Item):
    index=scrapy.Field()
    title=scrapy.Field()
    year=scrapy.Field()
    lang=scrapy.Field()
    sub=scrapy.Field()
    download_nb=scrapy.Field()
    score=scrapy.Field()
    user_score=scrapy.Field()

class Allocine(scrapy.Spider):
    name = 'allocine'
    custom_settings={
         'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
         'FEED_FORMAT': 'jsonlines',
         'FEED_URI': 'teamMKV_movies_with_scores.json',
         'DOWNLOAD_DELAY': 1.5
    }
    
    def movie_lookup(self,parsed_json,index):
        for movie in parsed_json:
            if movie['index'] == index:
                return movie
                break
        raise KeyError

    def start_requests(self):
        with open(TEAMMKV_OUTPUT_FILE) as teammkv_file:
            teamMkv_data = json.load(teammkv_file)
            with open(NEW_MOVIES_FILE) as f:
                for index, title in json.load(f).items():
                    movie_info = self.movie_lookup(teamMkv_data, index)
                    yield scrapy.Request(url='http://www.allocine.fr/recherche/?q='+title, meta={'movie_info': movie_info})

    def parse(self, response):
        table_1 = response.xpath('//table')[0]
        movies = table_1.xpath('.//tr[td/div/div/span]')
        movie_info = response.meta['movie_info']
        for m in movies.extract():
            selector = Selector(text=m)
            for span in selector.xpath('.//span'):
                if remove_tags(span.extract().split()[2]).startswith(movie_info['year']):
                    yield response.follow(selector.xpath('.//a/@href').extract_first(), callback=self.parse_main, meta=response.meta)


    def parse_main(self, response):
        item_cont=response.xpath('//div[@class="rating-item-content"]')
        ms = Movie_Score()
        movie_info = response.meta['movie_info'] 
        for key, value in movie_info.items():
            ms[key] = value 
        first_element, second_element = None, None
        if len(item_cont) == 2:
            first_element, second_element = [item_cont[i].xpath('span/text()').extract_first() for i in range(2)]
        elif len(item_cont) == 1:
            first_element = item_cont[0].xpath('span/text()').extract_first()
        if first_element:
            if first_element.strip() == 'Presse':
                movie_info['score']=item_cont[0].xpath('.//span[@class="stareval-note"]/text()').extract_first().strip()
                if second_element:
                    if second_element.strip() == 'Spectateurs':
                            movie_info['user_score']=item_cont[1].xpath('.//span[@class="stareval-note"]/text()').extract_first().strip()
            else:
                movie_info['score']=None
                if first_element.strip() == 'Spectateurs':
                    movie_info['user_score']=item_cont[0].xpath('.//span[@class="stareval-note"]/text()').extract_first().strip()
                else:
                    movie_info['user_score']=None


            
