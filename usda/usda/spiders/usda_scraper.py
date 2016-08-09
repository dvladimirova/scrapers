# -*- coding: utf-8 -*-
import scrapy

from usda.items import UsdaItem


class UsdaScraperSpider(scrapy.Spider):
    name = "usda_scraper"
    allowed_domains = ["usda.gov"]
    start_urls = (
        'https://ndb.nal.usda.gov/ndb/foods',
    )

    pageStartUrl = 'https://ndb.nal.usda.gov';

    def parse(self, response):
        for row in response.xpath('//*[@id="pageBodyWide"]/div[5]/div[1]/table/tbody/tr'):
            ndbId = row.xpath('td[1]/a/text()').extract()
            name = row.xpath('td[2]/a/text()').extract()
            group = row.xpath('td[3]/text()').extract()
            item = UsdaItem()
            item['ndbId'] = ndbId[0]
            item['name'] = name[0]
            item['group'] = group[0]
            href = row.xpath('td[2]/a/@href').extract()
            url = response.urljoin(href[0])
            yield scrapy.Request(url, callback=self.parse_food, meta={'item': item})
        for link in response.css('body > div.bodywrapper > form#quickform > div#pageBodyWide > div.paginateButtons > a'):
            nextClass = link.xpath('@class').extract()
            if nextClass[0] == 'nextLink':
                url = link.xpath('@href').extract()
                nextPageUrl = ''.join([self.pageStartUrl, url[0]])
                yield scrapy.Request(nextPageUrl, callback=self.parse)

        
    def parse_food(self, response):
        item = response.meta['item']
        item['nutrients'] = {}
        nutrient = None
        for row in response.css('body > div.bodywrapper > div.wbox > div.menuButton div > form > div > table > tbody > tr'):
            cl = row.xpath('@class').extract()
            if not cl or cl[0] == 'even':
                nutrient = row.xpath('td/text()').extract()[0]
            else:
                item['nutrients'].setdefault(nutrient, []).append({
                    'name': row.xpath('td[1]/text()').extract()[0].strip(),
                    'unit': row.xpath('td[2]/text()').extract()[0].strip(),
                    'value': row.xpath('td[3]/text()').extract()[0].strip()
                })

        yield item


