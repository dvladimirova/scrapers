# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CookstrItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
    image = scrapy.Field()
    ingredients = scrapy.Field()
    directions = scrapy.Field()
    meta = scrapy.Field()