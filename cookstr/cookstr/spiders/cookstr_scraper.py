# -*- coding: utf-8 -*-
import scrapy
import collections
import urllib

from cookstr.items import CookstrItem

class CookStrSpider(scrapy.Spider):
    name = 'cookstr'
    allowed_domains = ['cookstr.com']
    search_url = 'http://www.cookstr.com/?task=search&search_type=standard&is_form=1&search_term=%s'
    foods = [
        'beef',
        'lamb',
        'rabbit',
        'veal',
        'pork',
        'chicken',
        'fish',
        'turkey',
        'cheese',
        'eggs',
        'yogurt',
        'arugula',
        'avocado',
        'beans',
        'beets',
        'bok choy',
        'broccoli',
        'brussels sprouts',
        'cabbage',
        'cauliflower',
        'cucumber',
        'eggplant',
        'fennel',
        'leeks',
        'lettuce',
        'mushroom',
        'onion',
        'pepper',
        'spinach',
        'summer squash',
        'zucchini',
        'bulgur',
        'corn',
        'rice',
        'buckwheat',
        'quinoa',
        'parsnip',
        'potato',
        'pumpkin',
        'acorn squash',
        'butternut squash',
        'green peas',
        'lentils',
        'flour',
        'pasta',
        'noodles',
        'couscous',
        'bread',
        'pizza',
        'tortillas',
        'fruit'
    ]

    def start_requests(self):
        for food in self.foods:
            url = self.search_url % urllib.quote_plus(food)
            yield scrapy.Request(url, callback=self.parse, meta={'food': food}) 

    def parse(self, response):
        for link in response.css('body > div.mainLayout > section.mainContent > div > div.articleList > div.articleList2 > div.articleDiv > div > div.mainImgDiv > div.focal-point > div > a'):
            url = link.xpath('@href').extract()
            yield scrapy.Request(response.urljoin(url[0]), callback=self.parse_recipe, meta={'food': response.meta['food']})

        for link in response.xpath('//*[@id="categoryArticles"]/div[4]/ul/li/a'):
            nextClass = link.xpath('span/@class').extract()
            if nextClass[0] == 'link next':
                url = link.xpath('@href').extract()
                yield scrapy.Request(response.urljoin(url[0]), callback=self.parse, meta={'food': response.meta['food']})

    def parse_recipe(self, response):
        # check if this is a multi-recipe page
        for link in response.css('body > div > section.mainContent > div > div.articleDiv > div.stepByStepInstructionsDiv > div.sections > div.section > div.cells > div.decimal > div.articleAttrSection > p > a'):
            url = link.xpath('@href').extract()
            yield scrapy.Request(response.urljoin(url[0]), callback=self.parse_recipe, meta={'food': response.meta['food']})

        item = CookstrItem()
        nameElement = response.css('body > div.mainLayout > section.mainContent > div > div.articleDiv > div.articleHeadlineDiv > h1')
        nameText = nameElement.xpath('text()').extract()
        item['name'] = nameText[0]
        item['category'] = response.meta['food']
        item['url'] = response.url
        imageElement = response.css('body > div.mainLayout > section.mainContent > div > div.articleDiv > div.mainImg > img')
        imageText = imageElement.xpath('@src').extract()
        if imageText:
            item['image'] = ''.join(['http:', imageText[0]])
        item['ingredients'] = []
        ingredient = None
        for row in response.css('body > div.mainLayout > section.mainContent > div > div.articleDiv > div.recipeIngredients > ul > li'):
            ingredientText = row.xpath('text()').extract()
            text = ''
            if ingredientText:
                text = ingredientText
            if ingredientText and isinstance(ingredientText, collections.Sequence):
                text = ingredientText[0]
            span = row.xpath('span')
            ingredient = {}
            if span:
                cl = row.xpath('span/@class').extract()
                if cl and cl[0] == 'ingredient':
                    ingredient['value'] = text.strip()
                    ingredient['ingredient'] = row.xpath('span/text()').extract()[0].strip()
                else:
                    ingredient['value'] = ''
                    ingredient['ingredient'] = text.strip()
            else:
                ingredient['value'] = ''
                ingredient['ingredient'] = text.strip()
            item['ingredients'].append(ingredient)
        item['directions'] = []
        direction = None
        for row in response.css('body > div.mainLayout > section.mainContent > div > div.articleDiv > div.stepByStepInstructionsDiv > div.sections > div.section > div.cells > div > div.articleAttrSection > p'):
            direction = row.xpath('text()').extract()
            if (direction):
                item['directions'].append(direction[0])

        item['meta'] = []
        for row in response.css('body > div.mainLayout > section.mainContent > div > div.articleDiv .attrLabel'):
            label = row.xpath('text()').extract()[0]
            parent = row.xpath('..')
            value = parent.xpath('text()')
            if not value:
                value = parent.xpath('span[2]/text()')
            item['meta'].append({'property': label, 'value': value.extract()[0]})

        skill = response.css('body > div.mainLayout > section.mainContent > div > div.articleDiv .articleAttrSection img')
        if skill:
            item['meta'].append({'property': 'cooking_skill', 'value': skill.xpath('@alt').extract()[0]})

        yield item