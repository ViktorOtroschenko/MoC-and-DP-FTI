# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    full_name = scrapy.Field()
    photo = scrapy.Field()
    is_followed_by = scrapy.Field()
    follows = scrapy.Field()