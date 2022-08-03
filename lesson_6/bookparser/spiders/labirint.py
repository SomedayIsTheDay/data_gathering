import scrapy
from scrapy.http import HtmlResponse
import hashlib
from lesson_6.bookparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = "labirint"
    allowed_domains = ["labirint.ru"]
    start_urls = [
        "https://www.labirint.ru/search/"
        "%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/?stype=0"
    ]

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath("//a[@class='pagination-next__text']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@class='cover']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    @staticmethod
    def book_parse(response: HtmlResponse):
        name = response.xpath("//div[@id='product-title']/h1/text()").get()
        link = response.url
        _id = hashlib.md5(link.encode()).hexdigest()
        author = response.xpath("//a[@data-event-label='author']/text()").get()
        price = response.xpath(
            "//span[@class='buying-priceold-val-number']/text()"
        ).get()
        discounted_price = response.xpath(
            "//span[@class='buying-pricenew-val-number']/text()"
        ).get()
        rating = response.xpath("//div[@id='rate']/text()").get()
        yield BookparserItem(
            name=name,
            link=link,
            _id=_id,
            author=author,
            price=price,
            discounted_price=discounted_price,
            rating=rating,
        )
