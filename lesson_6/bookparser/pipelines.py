# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BookparserPipeline:
    def __init__(self):
        client = MongoClient("localhost", 27017)
        self.mongo_base = client["bookparser"]

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.update_one({"_id": item["_id"]}, {"$set": item}, upsert=True)
        return item
