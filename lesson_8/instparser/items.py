# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst


class InstparserItem(scrapy.Item):
    username = scrapy.Field(output_processor=TakeFirst())
    pfp_url = scrapy.Field(output_processor=TakeFirst())
    user_id = scrapy.Field(output_processor=TakeFirst())
    status = scrapy.Field(output_processor=TakeFirst())
    user_being_parsed = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
