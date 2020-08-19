# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient, errors

import scrapy
from scrapy.pipelines.images import ImagesPipeline


class DataBasePipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlin_scrapy


    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.update_one({'name': item['name']}, {'$set': item}, upsert=True)
        return item


class LeroymerlinPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img.get(), meta=item)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item