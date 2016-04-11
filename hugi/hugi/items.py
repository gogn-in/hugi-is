# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HugiArticle(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    type = scrapy.Field()
    category = scrapy.Field()
    id = scrapy.Field()
    comments = scrapy.Field()
    commentcount = scrapy.Field()
    body = scrapy.Field()


class HugiUser(scrapy.Item):
    username = scrapy.Field()
    url = scrapy.Field()
    stats = scrapy.Field()
    points = scrapy.Field()
    date_joined = scrapy.Field()
    id = scrapy.Field()

