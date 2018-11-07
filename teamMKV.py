import scrapy, re
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose, Identity
from scrapy.loader import ItemLoader
from functools import partial

def lang_sub_processor(regex, group_idx):  
    if regex.group(group_idx): 
        return regex.group(group_idx).split('-')
    else:
        return ''

class Movie(scrapy.Item):
    index=scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=MapCompose(lambda x : x.split()[-1]),
    )
    title=scrapy.Field(
        output_processor=MapCompose(lambda x : ' '.join(x.group(1).split('.')).strip()),
    )
    year=scrapy.Field()
    lang=scrapy.Field(
        output_processor=MapCompose(partial(lang_sub_processor,group_idx=3)),
    )
    sub=scrapy.Field(
        output_processor=MapCompose(partial(lang_sub_processor,group_idx=4)),
    )

class TeamMKV(scrapy.Spider):
    name = 'teamMKV'
    start_urls = ['http://xdcclist.us.to/?team=Team-MKV&xdcc_id=1']

    def parse(self, response):
        for tr_elem in response.xpath('//tr[position() > 1]'):
            il = ItemLoader(item=Movie())
            parsed_pack = tr_elem.xpath('./td[position() = 1]').extract()
            parsed_data = tr_elem.xpath('./td[position() = 2]/b/a/@title').extract_first()
            loader = ItemLoader(Movie(), tr_elem)
            m = re.match('(.*)([0-9]{4}).*\.[\[{][^{]*\}(?:\{([^{]*)\})?(?:\{Sub\.(.*)})?',parsed_data)
            il.add_value('index', parsed_pack)
            il.add_value('title', m) 
            il.add_value('year', m.group(2))
            il.add_value('lang', m)
            il.add_value('sub', m)
            yield il.load_item()
