"""Contains background tasks used in the app."""
from functools import partial
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
        results: ProductSearchResultT,
        batch_size: int = 24) -> None:
    """Background task for adding product records to the db."""
    logger.debug(
        "Running background task to save the retrieved product results...")
    products = []
    product_data = []
    for result in results:
        products.extend(
            list(map(lambda x: x[0], result[1])))
        product_data.extend(
            list(map(lambda x: (x[1], result[0]["store_id"]), result[1])))

    print(products)
    print(product_data)


def save_products(products: list[schemas.Product]):
    pass


def save_product_data(product_data: list[schemas.ProductData]):
    pass