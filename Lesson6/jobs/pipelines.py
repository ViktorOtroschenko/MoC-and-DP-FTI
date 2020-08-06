# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from pymongo import MongoClient, errors

class JobsPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy_scrapy

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            self.process_hh_item(item, spider.name)
        if spider.name == 'sjru':
            self.process_sj_item(item, spider.name)
        return item

    def write_to_db(self, vacancy, collection_name):
        collection = self.mongo_base[collection_name]
        try:
            collection.insert_one(vacancy)
        except errors.DuplicateKeyError:
            print("Duplicate found for vacancy: ", vacancy)
            pass