from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from spiders.instagram import InstagramSpider


def users():
    users_to_parse = []
    while True:
        user = input("Enter the username you want to find or leave blank to quit: ")
        if user == "":
            break
        users_to_parse.append(user)
    return users_to_parse


if __name__ == "__main__":
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    runner.crawl(InstagramSpider, users_to_parse=users())
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
