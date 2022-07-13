# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
class WebberPipeline:

    product_list = []

    def process_item(self, item, spider):
        self.update_list(item)

    @classmethod
    def update_list(cls, item):
        cls.product_list.append(item)
