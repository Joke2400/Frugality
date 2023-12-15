"""Contains background tasks used in the app."""
from itertools import islice
from typing import Iterable
from app.core.orm import schemas, crud
from app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)
ProductSearchResultT = \
    list[
        tuple[
            dict[str, str | int],
            list[
                tuple[
                    schemas.Product,
                    schemas.ProductData
                ]
            ]
        ]
    ]


def batched(iterable: Iterable, batch_size: int):
    if batch_size < 1:
        raise ValueError("Batch size must be at least 1.")
    it = iter(iterable)
    while batch := tuple(islice(it, batch_size)):
        yield batch


def save_store_results(stores: list[schemas.Store]) -> None:
    """Background task for adding store records to the db.
    TODO: Add batched/bulk inserts
    """
    logger.debug(
        "Running background task to save the retrieved store results...")
    total_count = len(stores)
    success_count = 0
    for store in stores:
        if crud.add_store_record(store):
            success_count += 1
    logger.debug(
        "Added %s stores out of a total of %s to db. %s",
        success_count, total_count,
        f"Remaining: {total_count-success_count}")


def save_product_results(
        results: ProductSearchResultT) -> None:
    """Background task for adding product records to the db."""
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
