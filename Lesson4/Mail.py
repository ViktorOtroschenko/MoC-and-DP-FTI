import requests
from lxml import html
from pymongo import MongoClient
from pprint import pprint

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/84.0.4147.89 Safari/537.36'}
client = MongoClient('localhost', 27017)
db = client['mail_news']

def mail_news():
    main_link = 'https://news.mail.ru'
    response = requests.get(main_link, headers=header)
    dom = html.fromstring(response.text)
    links = dom.xpath("//div[@class='daynews__item']/a/@href")
    links += dom.xpath("//a[@class='list__text']/@href")

    news = []
    for link in links:
        new = {}
        new['link'] = main_link + link
        if 'http' in link:
            response = requests.get(link, headers=header)
        else:
            response = requests.get(main_link + link, headers=header)
        dom = html.fromstring(response.text)
        new['source'] = dom.xpath("//span[@class='breadcrumbs__item']//span[@class='link__text']/text()")[0]
        new['text'] = dom.xpath("//h1/text()")[0]
        new['date'] = dom.xpath("//span[@class='note__text breadcrumbs__text js-ago']/@datetime")[0][:10]
        news.append(new)
    return news

pprint(mail_news())

mail_news_db = db.mail_news
mail_news_db.insert_many(mail_news())
