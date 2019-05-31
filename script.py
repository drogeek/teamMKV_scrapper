import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from teamMKV import TeamMKV
from allocine import Allocine, SCORED_TEAMMKV_OUTPUT_FILE
import os, json, notify2

OLD_TEAMMKV_OUTPUT_FILE='.previousteamMKV_movies.json'
TEAMMKV_OUTPUT_FILE='teamMKV_movies.json'
NEW_MOVIES_FILE='new_movies.json'
configure_logging()
runner = CrawlerRunner()

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
        with open(SCORED_TEAMMKV_OUTPUT_FILE,'r') as f:
            scoredJson = [ json.loads(l) for l in f.readlines() ]
            indexDifference = set(x[0] for x in difference)
            print(list(filter(lambda x : x['index'] in indexDifference, scoredJson)))

    reactor.stop()

crawl()
reactor.run()
