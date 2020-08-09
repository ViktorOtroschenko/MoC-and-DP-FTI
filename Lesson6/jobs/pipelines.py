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

    def process_hh_item(self, item, collection_name):
        vacancy = {
            'name': item['name'],
            'salary_from': self.get_hh_salary_from(item),
            'salary_to': self.get_hh_salary_to(item),
            'currency': self.get_hh_currency(item),
            'link': item['link'],
            'source_site': item['source_link']
        }
        vacancy['_id'] = self.make_hash(vacancy)
        self.write_to_db(vacancy, collection_name)

    def get_hh_salary_from(self, item):
        if 'salary' not in item:
            return None

        salary = item['salary']

        if len(salary) < 2:
            return None

        if 'от ' in salary[0]:
            return int(salary[1].replace(' ', '').replace('\xa0', ''))

    def get_hh_salary_to(self, item):
        if 'salary' not in item:
            return None

        salary = item['salary']

        if len(salary) < 2:
            return None

        if ' до ' in salary:
            return int(salary[3].replace(' ', '').replace('\xa0', ''))

    def get_hh_currency(self, item):
        if 'salary' not in item:
            return None

        salary = item['salary']

        if len(salary) < 2:
            return None

        if 'от ' in salary[0] and ' до ' in salary[2]:
            return salary[5].replace(' ', '').replace('\xa0', '')

        if 'от ' in salary[0]:
            return salary[3].replace(' ', '')

    # Superjob methods

    def process_sj_item(self, item, collection_name):
        vacancy = {
            'name': item['name'],
            'salary_from': self.get_sj_salary_from(item),
            'salary_to': self.get_sj_salary_to(item),
            'currency': self.get_sj_currency(item),
            'link': item['link'],
            'source_site': f"https://superjob.ru{item['source_link']}"
        }
        vacancy['_id'] = self.make_hash(vacancy)
        self.write_to_db(vacancy, collection_name)

    def get_sj_salary_from(self, item):
        if 'salary' not in item:
            return None

        salary = item['salary']

        if len(salary) < 2:
            return None

        if 'от' in salary:
            return int(re.sub('[^\d]', '', salary[2]))

        return int(re.sub('[^\d]', '', salary[0]))

    def get_sj_salary_to(self, item):
        if 'salary' not in item:
            return None

        salary = item['salary']

        if len(salary) < 2:
            return None

        if 'от' not in salary:
            return int(re.sub('[^\d]', '', salary[1]))

    def get_sj_currency(self, item):
        if 'salary' not in item:
            return None

        salary = item['salary']

        if len(salary) < 2:
            return None

        if 'от' in salary:
            return re.sub('[\d\xa0\s]', '', salary[2])

        if 'от' not in salary:
            return re.sub('[\d\xa0\s]', '', salary[3])