"""Contains background tasks used in the app."""
from typing import Type
from itertools import batched
from app.core.orm import schemas, models, crud
from app.utils import LoggerManager

from app.core.typedefs import (
    ProductSearchResultT,
    PydanticSchemaInT,
    OrmModelT
)

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


def save_in_batches(
        items: list[PydanticSchemaInT], model: Type[OrmModelT],
        batch_size: int = 24) -> list[tuple[PydanticSchemaInT, ...]]:
    total_item_count: int = len(items)
    failed_count: int = 0
    failed_batches: list[tuple[PydanticSchemaInT, ...]] = []
    for batch in batched(iterable=items, n=batch_size):
        if not crud.bulk_create_records(records=batch, model=model):
            failed_count += len(batch)
            failed_batches.append(batch)
    logger.debug(
        "Saved %s item(s) out of a total of %s in batches. %s",
        total_item_count-failed_count, total_item_count,
        f"Remaining: {failed_count}")
    return failed_batches


def save_store_results(stores: list[schemas.Store]) -> None:
    """Background task for adding store records to the db.
    TODO: Add batched/bulk inserts
    """
    logger.debug(
        "Running background task to save the retrieved store results...")
    remainder = save_in_batches(
        items=stores, model=models.Store, batch_size=50)
    if len(remainder) == 0:
        return None
    logger.debug(
        "Saving the remaining %s stores individually...",
        len(remainder))
    failed_count: int = 0
    for batch in remainder:
        for store in batch:
            if not crud.create_record(record=store, model=models.Store):
                failed_count += 1
    logger.debug(
        "Saved %s out of the remaining %s stores. %s",
        len(remainder)-failed_count, len(remainder),
        f"Unable to add {failed_count} stores, ignoring...")
        

def save_product_results(
        results: ProductSearchResultT) -> None:
    """Background task for adding product records to the db."""
    pass
    logger.debug(
        "Running background task to save the retrieved product results...")
    products, product_data = [], []
    for result in results:
        for item_tuple in result[1]:
            products.append(item_tuple[0])
            product_data.append(
                (item_tuple[1],               # ProductData
                 int(result[0]["store_id"]),  # Store ID
                 item_tuple[0].ean))          # Product EAN
    save_products(products=products)
    save_product_data(data=product_data)


def save_products(products: list[schemas.Product]):
    pass
    total_count = len(products)
    success_count = 0
    for product in products:
        if crud.add_product_record(product=product):
            success_count += 1
    logger.debug(
        "Added %s products out of a total of %s to db. %s",
        success_count, total_count,
        f"Remaining: {total_count-success_count}")


def save_product_data(data: list[tuple[schemas.ProductData, int, str]]):
    pass
    total_count = 0
    failed_batch_count = 0
    failed_item_count = 0
    failed_batches = []
    for batch in batched(data, batch_size=50):
        total_count += len(batch)
        if not crud.bulk_add_product_data_records(batch):
            failed_batch_count += 1
            failed_batches.append(batch)

    failed = []
    for batch in failed_batches:
        for item in batch:
            if not crud.add_product_data_record(item):
                failed_item_count += 1
                failed.append(item)
