import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from leroy_parser.items import LeroymerlinItem

class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel='next']/@href").extract_first()
        goods_links = response.xpath("//product-card/@data-product-url").extract()
        for link in goods_links:
            yield response.follow(link, callback=self.item_parse)

        yield response.follow(next_page, callback=self.parse)

    def item_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath('name', '//h1[@itemprop="name"]/text()')
        loader.add_xpath('parameters', '//div[@class="def-list__group"]')
        loader.add_xpath('photos', '//img[@itemprop="image"]/@src')
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_value('link', response.url)
        yield loader.load_item()
