# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose


def process_price(value):
    value = value.replace(" ", "")
    try:
        value = int(value)
    except ValueError:
        pass
    return value


def process_specs(spec):
    spec = spec.replace("\n", "").strip()
    return spec


class HouseparserItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    price = scrapy.Field(
        input_processor=MapCompose(process_price), output_processor=TakeFirst()
    )
    currency = scrapy.Field(
        input_processor=MapCompose(process_price), output_processor=TakeFirst()
    )
    spec_labels = scrapy.Field(input_processor=MapCompose(process_specs))
    spec_values = scrapy.Field(input_processor=MapCompose(process_specs))
    specs = scrapy.Field()
