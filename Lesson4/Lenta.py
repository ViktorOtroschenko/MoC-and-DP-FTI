import requests
from lxml import html
from pymongo import MongoClient
from pprint import pprint

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/84.0.4147.89 Safari/537.36'}
client = MongoClient('localhost', 27017)
db = client['lenta_news']

def lenta_news():
    main_link = 'https://lenta.ru'
    response = requests.get(main_link, headers=header)
    dom = html.fromstring(response.text)
    links = dom.xpath("//a/time")

    news = []
    for item in links:
        new = {}
        link = item.xpath("../@href")
        text = item.xpath("../text()")
        date = item.xpath("./@title")
        new['text'] = text[0].replace('\xa0', ' ')
        new['source'] = 'lenta.ru'
        new['date'] = date[0]

        if 'https://' in link[0]:
            new['link'] = link[0][:link[0].index('?')]
        else:
            new['link'] = main_link + link[0]

        news.append(new)

    return news

pprint(lenta_news())

lenta_news_db = db.lenta_news
lenta_news_db.insert_many(lenta_news())