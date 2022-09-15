from dataclasses import dataclass
from typing import Optional
from ....data.filepaths import FilePaths
from .foodie_pages import Page
from scrapy import Spider, Request
import datetime

class BaseSpider(Spider):

    name = "BaseSpider"

    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.data_manager = kwargs.get("data_manager")
        self.performed_searches = []
        self.saved_pages = []

    def start_requests(self):
        if self.start_urls is not None:
            for url in self.start_urls:
                request = self.scrape(url, self.parse)
                yield request

    def database_query(self, command, **kwargs):
        func = command(receiver=self.data_manager, payload=kwargs)
        result = func.execute()
        return result

    def create_page(self, response, page_class):
        page = page_class(response)
        self.saved_pages.append(page)
        return page

    def scrape(self, search, url, callback, meta):
        self.performed_searches.append(url)
        cb_kwargs = {
            "start_time": datetime.datetime.now(),
            "search": search}
        request = Request(url=url, callback=callback, meta=meta,
                          cb_kwargs=cb_kwargs, dont_filter=True)
        return request

    def basic_response_print(self, callback, func):
        def wrapper(response, **kwargs):
            end_time = datetime.datetime.now()
            timedelta = end_time - kwargs.get("start_time")
            duration = f"{timedelta.seconds}s {int(str(timedelta.microseconds)[:3])}ms"
            print(f"\n[RESPONSE]: '{response.status}' from IP: '{response.ip_address}' (Took: {duration}).")
            func(response)
            return callback(response, **kwargs)
        return wrapper

    def advanced_response_print(self, callback, func):
        func = self.basic_response_print(callback=callback, func=func)
        return func

    def parse(self, response, **kwargs):
        page = self.create_page(response, Page)
        print(page.source_url)
        with open(FilePaths.response_path, 'w') as file:
            file.write(response.text)


# TODO: Read up on both dataclasses and type hinting
# Type hinting: https://peps.python.org/pep-0526/, https://mypy.readthedocs.io/en/stable/class_basics.html#instance-and-class-attributes, https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
#https://docs.python.org/3/howto/annotations.html
@dataclass 
class SpiderSearch:

    store_name: str
    requested_products: list[str]
    store_select: Optional[str]

    def __post_init__(self):
        self.display_name = self.store_name.strip()
        self.store_name = self.display_name.lower()

    def __str__(self):
        return f"{self.store_name},{self.store_select}"