# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StoreItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    chain = scrapy.Field()
    open_times = scrapy.Field()

    address = scrapy.Field()
    location = scrapy.Field()

    date_added = scrapy.Field()
    last_updated = scrapy.Field()

    href = scrapy.Field()
    select = scrapy.Field()
    
class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    store_name = scrapy.Field()
    name = scrapy.Field()
    subname = scrapy.Field()
    img = scrapy.Field()
    href = scrapy.Field()
    quantity = scrapy.Field()
    price = scrapy.Field()
    unit = scrapy.Field()
    unit_price = scrapy.Field()
    shelf_name = scrapy.Field()
    shelf_href = scrapy.Field()
    
    date_added = scrapy.Field()
    last_updated = scrapy.Field()