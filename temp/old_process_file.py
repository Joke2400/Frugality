import os
from webscraper.data.filepaths import FilePaths
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from webscraper.webscraper_package.spiders.webber import Webber
from webscraper.data_manager_package.data_manager import DataManager

def start(products, stores, limit=25, reset=False):
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', FilePaths.settings_path)
    try:
        os.remove(FilePaths.log_path) #Remove scrapy log file from previous run
    except:
        pass
    process = CrawlerProcess(get_project_settings())

    data_manager = DataManager(path=FilePaths.database_path)
    if reset:
        data_manager.reset_database()

    process.crawl(Webber, 
            requested_products=products,
            requested_stores=stores, 
            limit=limit,
            data_manager=data_manager,
            requesting_old_site=True
            )

    process.start()
    data_manager.close_session()

    