# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CampusfranceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    titre = scrapy.Field()
    labo = scrapy.Field()
    annee = scrapy.Field()
    programme = scrapy.Field()
    domaine = scrapy.Field()
