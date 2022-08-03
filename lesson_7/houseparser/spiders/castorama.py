import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from items import HouseparserItem


class CastoramaSpider(scrapy.Spider):
    name = "castorama"
    allowed_domains = ["castorama.ru"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [
            f"https://www.castorama.ru/catalogsearch/result/?q={kwargs.get('search')}"
        ]

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath("//a[@title='След.']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@class='product-card__img-link']/@href")
        for link in links:
            yield response.follow(link, callback=self.product_parse)

    @staticmethod
    def product_parse(response):
        loader = ItemLoader(item=HouseparserItem(), response=response)
        loader.add_xpath("name", "//h1[@itemprop='name']/text()")
        loader.add_xpath(
            "price",
            "//div[contains(@class,'add-to-cart__price ')]//span[@class='price']/child::*/span[1]/text()",
        )
        loader.add_xpath(
            "currency",
            "//div[contains(@class,'add-to-cart__price ')]//span[@class='currency']/text()",
        )
        loader.add_value("url", response.url)
        loader.add_xpath(
            "photos",
            "//img[contains(@class,'top-slide__img')]/@data-src",
        )
        loader.add_xpath(
            "spec_labels",
            "//div[@id='specifications']//span[contains(@class, 'specs-table__attribute-name')]/text()",
        )
        loader.add_xpath(
            "spec_values",
            "//div[@id='specifications']//dd[contains(@class, 'specs-table__attribute-value')]/text()",
        )

        yield loader.load_item()
