import scrapy
from scrapy.http import HtmlResponse
from jobs.items import JobsItem

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response:HtmlResponse):
        next_page = response.css(
            'a.icMQ_._1_Cht._3ze9n.f-test-button-dalshe.f-test-link-Dalshe::attr(href)'
        ).extract_first()

        vacancy_links = response.css('a.icMQ_._6AfZ9._2JivQ._1UJAN::attr(href)').extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.vacansy_parse)
        yield response.follow(next_page, callback=self.parse)

    def vacansy_parse(self, response:HtmlResponse):
        name_job = response.xpath('//h1/text()').extract_first()
        salary_job = response.css('div._3MVeX span._1OuF_.ZON4b span._3mfro._2Wp8I.PlM3e._2JVkc::text').extract()
        link = response.url
        source_link = response.css('a.icMQ_._2JivQ::attr(href)').extract_first()
        yield JobsItem(name=name_job, salary=salary_job, link=link, source_link=source_link)
