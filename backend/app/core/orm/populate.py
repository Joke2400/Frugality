"""Contains functions that populate the database with test data."""
from datetime import timezone, datetime, timedelta
from backend.app.utils import LoggerManager
from . import crud
from . import models


logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


def populate_db() -> None:
    """Populate the database with consistent test data."""
    logger.info("Populating the database with test data...")
    populate_stores()
    populate_products()


def populate_stores() -> None:
    """Populate the database with a consistent set of stores."""
    stores = [
        {
            "store_id": 542862479,
            "store_name": "Prisma Olari",
            "slug": "prisma-olari",
            "brand": "prisma"
        },
        {
            "store_id": 647396324,
            "store_name": "Prisma Iso Omena",
            "slug": "prisma-iso-omena",
            "brand": "prisma"
        },
        {
            "store_id": 515451524,
            "store_name": "S-market Olari",
            "slug": "s-market-olari",
            "brand": "s-market"
        },
        {
            "store_id": 697942431,
            "store_name": "S-market Lähderanta",
            "slug": "s-market-lahderanta",
            "brand": "s-market"
        },
    ]
    for i in stores:
        assert crud.create_record(record=i, model=models.Store) is True
    logger.info("Populated the database with test stores.")


def populate_products() -> None:
    """Populate the database with a consistent set of products."""
    products = [
        {
            "ean": "6414893500167",
            "name": "Kotimaista naudan jauheliha 700 g",
            "slug": "kotimaista-naudan-jauheliha-700-g",
            "category": "Naudan jauheliha",
            "brand": "Kotimaista",
        },
        {
            "ean": "6415712506117",
            "name": "Kotimaista täysmaito 1l",
            "slug": "kotimaista-taysmaito-1l",
            "category": "Maidot",
            "brand": "Kotimaista",
        },
        {
            "ean": "6408430011667",
            "name": "Valio kevytmaito 1 l laktoositon UHT",
            "slug": "valio-kevytmaito-1-l-laktoositon-uht",
            "category": "Laktoosittomat ja vähälaktoosiset maidot",
            "brand": "Valio",
        }
    ]
    product_data = [
        {
            "eur_unit_price_whole": 6,
            "eur_unit_price_decimal": 75,
            "eur_cmp_price_whole": 9,
            "eur_cmp_price_decimal": 64,
            "label_unit": "KPL",
            "comparison_unit": "kg",
            "store_id": 542862479,
            "product_ean": "6414893500167"
        },
        {
            "eur_unit_price_whole": 7,
            "eur_unit_price_decimal": 39,
            "eur_cmp_price_whole": 10,
            "eur_cmp_price_decimal": 56,
            "label_unit": "KPL",
            "comparison_unit": "kg",
            "store_id": 697942431,
            "product_ean": "6414893500167"
        },
        {
            "eur_unit_price_whole": 1,
            "eur_unit_price_decimal": 38,
            "eur_cmp_price_whole": 1,
            "eur_cmp_price_decimal": 38,
            "label_unit": "KPL",
            "comparison_unit": "L",
            "store_id": 697942431,
            "product_ean": "6415712506117"
        },
        {
            "eur_unit_price_whole": 2,
            "eur_unit_price_decimal": 39,
            "eur_cmp_price_whole": 2,
            "eur_cmp_price_decimal": 39,
            "label_unit": "KPL",
            "comparison_unit": "L",
            "store_id": 542862479,
            "product_ean": "6408430011667"
        },
        {
            "eur_unit_price_whole": 2,
            "eur_unit_price_decimal": 45,
            "eur_cmp_price_whole": 2,
            "eur_cmp_price_decimal": 45,
            "label_unit": "KPL",
            "comparison_unit": "L",
            "store_id": 697942431,
            "product_ean": "6408430011667",
            "timestamp": datetime.now(timezone.utc) - timedelta(days=2)
        }
    ]
    for x in products:
        assert crud.create_record(record=x, model=models.Product) is True
    logger.info("Populated the database with test products.")
    for y in product_data:
        assert crud.create_record(record=y, model=models.ProductData) is True
    logger.info("Populated the database with test product_data.")
