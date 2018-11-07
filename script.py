import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from teamMKV import TeamMKV
from allocine import Allocine
import os, json, notify2

OLD_TEAMMKV_OUTPUT_FILE='teamMKV_movies.json.old'
TEAMMKV_OUTPUT_FILE='teamMKV_movies.json'
NEW_MOVIES_FILE='new_movies.json'
configure_logging()
runner = CrawlerRunner({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_URI': TEAMMKV_OUTPUT_FILE,
    'FEED_FORMAT': 'json',
    'ROBOTSTXT_OBEY': 'False',
    'LOG_ENABLED': 'True'
})

@defer.inlineCallbacks
def crawl():
    difference = set()
    notify2.init('TeamMKV script')
    
    if os.path.exists(TEAMMKV_OUTPUT_FILE):
        os.rename(TEAMMKV_OUTPUT_FILE, OLD_TEAMMKV_OUTPUT_FILE)
        print('Generating {}'.format(TEAMMKV_OUTPUT_FILE))
        yield runner.crawl(TeamMKV)
        with open(OLD_TEAMMKV_OUTPUT_FILE) as old_file:
            with open(TEAMMKV_OUTPUT_FILE) as new_file:
                new_movies = json.load(new_file)
                new_movies_title_set = set((x['index'],x['title']) for x in new_movies)
                old_movies_title_set = set((x['index'],x['title']) for x in json.load(old_file))
                difference = new_movies_title_set.difference(old_movies_title_set)
                
    else:
        print('Generating {}'.format(TEAMMKV_OUTPUT_FILE))
        yield runner.crawl(TeamMKV)
        with open(TEAMMKV_OUTPUT_FILE) as new_file:
            new_movies = json.load(new_file)
            new_movies_title_set = set((x['index'],x['title']) for x in new_movies)
            difference = new_movies_title_set
    if difference:
        notifier = notify2.Notification("New movies available",'',"notification-message-im")
        notifier.show()
        with open(NEW_MOVIES_FILE,'w') as f:
            json.dump(dict(difference),f)
        print("new movies available: {}".format(difference))

    yield runner.crawl(Allocine)
    reactor.stop()

crawl()
reactor.run()
