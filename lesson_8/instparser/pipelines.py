# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
from pymongo import MongoClient


class InstparserPipeline:
    def __init__(self):
        client = MongoClient("localhost", 27017)
        self.mongo_base = client["instparser"]

    def process_item(self, item, spider):
        _id = hashlib.md5((item["username"] + item["status"]).encode()).hexdigest()
        user_being_parsed = item.pop("user_being_parsed")
        new_item = {"_id": _id, user_being_parsed: item}
        collection = self.mongo_base[spider.name]
        collection.update_one(
            {"_id": new_item["_id"]},
            {"$set": new_item},
            upsert=True,
        )
        return item
