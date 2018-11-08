import scrapy, re
from w3lib.html import remove_tags
from scrapy.loader.processors import Compose,MapCompose, Identity, Join
from scrapy.loader import ItemLoader
from functools import partial

def lang_sub_processor(regex, group_idx):  
    if regex.group(group_idx): 
        return regex.group(group_idx).split('-')
    else:
        return None

class Movie(scrapy.Item):
    index=scrapy.Field(
        input_processor=MapCompose(remove_tags,lambda x : x.split()[-1]),
        output_processor=Join(),
    )
    title=scrapy.Field(
        input_processor=MapCompose(lambda x : ' '.join(x.group(1).split('.')).strip()),
        output_processor=Join(),
    )
    year=scrapy.Field(
        output_processor=Join(),
    )
    lang=scrapy.Field(
        output_processor=MapCompose(partial(lang_sub_processor,group_idx=3)),
    )
    sub=scrapy.Field(
        output_processor=MapCompose(partial(lang_sub_processor,group_idx=4)),
    )
    download_nb=scrapy.Field(
        input_processor=MapCompose(remove_tags,lambda x : x[1:]),
        output_processor=Join(),
    )

class TeamMKV(scrapy.Spider):
    name = 'teamMKV'
    start_urls = ['http://xdcclist.us.to/?team=Team-MKV&xdcc_id=1']
    custom_settings={
         'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
         'FEED_FORMAT': 'json',
         'FEED_URI': 'teamMKV_movies.json',
    }
    def parse(self, response):
        for tr_elem in response.xpath('//tr[position() > 1]'):
            il = ItemLoader(item=Movie())
            parsed_pack = tr_elem.xpath('./td[position() = 1]').extract_first()
            parsed_data = tr_elem.xpath('./td[position() = 2]/b/a/@title').extract_first()
            parsed_download_nb = tr_elem.xpath('./td[position() = 4]').extract_first()
            loader = ItemLoader(Movie(), tr_elem)
            m = re.match('(.*)([0-9]{4}).*\.[\[{][^{]*\}(?:\{([^{]*)\})?(?:\{Sub\.(.*)})?',parsed_data)
            il.add_value('index', parsed_pack)
            il.add_value('title', m) 
            il.add_value('year', m.group(2))
            il.add_value('lang', m)
            il.add_value('sub', m)
            il.add_value('download_nb',parsed_download_nb)
            yield il.load_item()
