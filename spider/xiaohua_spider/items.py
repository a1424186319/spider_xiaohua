# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class XiaohuaSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    folder_name = scrapy.Field()  #吉林大学珠海学院余文丽
    img_name = scrapy.Field()     #2019Clvqr.jpg
    img_url = scrapy.Field()      #https://www.aaa.com/api/2019Clvqr.jpg
    # img_bytes = scrapy.Field()   #b'\3e\01'
