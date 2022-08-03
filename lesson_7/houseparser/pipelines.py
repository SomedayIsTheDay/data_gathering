# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import hashlib
from scrapy.utils.python import to_bytes


class HouseparserPipeline:
    def __init__(self):
        client = MongoClient("localhost", 27017)
        self.mongo_base = client["Houseparser"]

    def process_item(self, item, spider):
        _id = hashlib.md5(item["url"].encode()).hexdigest()
        item["_id"] = _id
        specs = dict(zip(item["spec_labels"], item["spec_values"]))
        item["specs"] = specs
        item.pop("spec_labels", None)
        item.pop("spec_values", None)
        collection = self.mongo_base[spider.name]
        collection.update_one({"_id": item["_id"]}, {"$set": item}, upsert=True)
        return item


class HouseparserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item["photos"]:
            for img in item["photos"]:
                try:
                    yield Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item["photos"] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f"{info.spider.name}/{info.spider.search}/full/{item['name']}/{image_guid}.jpg"
