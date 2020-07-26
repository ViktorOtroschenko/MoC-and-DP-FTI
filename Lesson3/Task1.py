import pandas as pd
from pymongo import MongoClient
from pprint import pprint

data = pd.read_csv('search.csv')
#
client = MongoClient('127.0.0.1', 27017)
db = client['search_db']
collection = db['hh']
data.reset_index(inplace=True)
data_dict = data.to_dict("records")
collection.insert_many(data_dict)

# Поиск и вывод вакансий с необходимой зарплатой
def find_salary(salary):
    objects = collection.find({'max_salary': {'$gte': salary}})
    for obj in objects:
        pprint(obj)

salary = input('Введите желаемую зарплату: ')
find_salary(salary)

def search_salary(money_min, money_max):
    objects = collection.find({'$or': [{'min_salary': {'$gte': money_min}}, {'max_salary': {'$lte': money_max}}]})
    for obj in objects:
        pprint(obj)

money_min = input('Введите минимальную зарплату: ')
money_max = input('Введите максимальную зарплату: ')
search_salary(money_min, money_max)

db.collection.create_index('link', unique=True)

def new_add(data_dict):
   for i in data_dict:
       collection.update_one({'link': i['link']}, {'$set': i}, upsert=True)

new_add(data_dict)