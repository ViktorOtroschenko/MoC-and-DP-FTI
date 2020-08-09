import scrapy
from scrapy.http import HtmlResponse
from jobs.items import JobsItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://hh.ru/search/vacancy?L_save_area=true&clusters=true&enable_snippets=true&text=Python&showClusters=true'
    ]

    def parse(self, response:HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next.HH-Pager-Control::attr(href)').extract_first()
        vacancy_links = response.css('div.vacancy-serp div.vacancy-serp-item a.HH-LinkModifier::attr(href)').extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.vacansy_parse)
        yield response.follow(next_page, callback=self.parse)

    def vacansy_parse(self, response:HtmlResponse):
        name_job = response.xpath('//h1/text()').extract_first()
        salary_job = response.css('p.vacancy-salary span::text').extract()
        link = response.url
        source_link = response.xpath('//a[@data-qa="vacancy-company-name"]/@href)').get('data')
        yield JobsItem(name=name_job, salary=salary_job, link=link, source_link=source_link)
