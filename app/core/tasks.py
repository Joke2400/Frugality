"""Contains background tasks used in the app."""
from typing import Type, Sequence
from itertools import batched
from app.core.orm import schemas, models, crud
from app.utils import LoggerManager

from app.core.typedefs import (
    ProductSearchResultT,
    OrmModelT,
    SchemaInOrDict
)

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)

# TODO: Asynchronous operations


def save_one_by_one(
        items: Sequence[SchemaInOrDict], model: Type[OrmModelT]) -> int:
    """Add a sequence of items to the database one-by-one.

    Args:
        items (Sequence[SchemaInOrDict]):
            The sequence of items to be saved.
        model (Type[OrmModelT]):
            The type of the ORM model that the items will be converted to.

    Returns:
        int:
            Returns an int to indicate how many items could not be added.
    """
    failed_count: int = 0
    for store in items:
        if not crud.create_record(record=store, model=model):
            failed_count += 1
    return failed_count


def save_in_batches(
        items: Sequence[SchemaInOrDict], model: Type[OrmModelT],
        batch_size: int = 24) -> list[tuple[SchemaInOrDict, ...]]:
    """Convert a sequence into batches & add each batch to the database.

    Args:
        items (Sequence[SchemaInOrDict]):
            The sequence of items to be saved in batches.
        model (Type[OrmModelT]):
            The type of the ORM model that the items will be converted to.
        batch_size (int, optional):
            The size of each batch. Defaults to 24.

    Returns:
        list[tuple[SchemaInOrDict, ...]]:
            Returns the failed batches (if any) as a list of tuples.
    """
    logger.debug("Batch size set to %s", batch_size)
    total_item_count: int = len(items)
    failed_count: int = 0
    failed_batches: list[tuple[SchemaInOrDict, ...]] = []
    for batch in batched(iterable=items, n=batch_size):
        if not crud.bulk_create_records(records=batch, model=model):
            failed_count += len(batch)
            failed_batches.append(batch)
    logger.debug(
        "Saved %s item(s) out of a total of %s in batches. %s",
        total_item_count-failed_count, total_item_count,
        f"Remaining: {failed_count}")
    return failed_batches


def save_items(items: Sequence[SchemaInOrDict],
               model: Type[OrmModelT]) -> None:
    """Background task for saving records into the database.

    Attempts to add the records in batches using a bulk insert.
    For each failed batch, attempt to add that batch's records
    individually.

    Args:
        items (list[SchemaInOrDict]):
            The list of items to be saved to the database.
    """
    remainder = save_in_batches(
        items=items, model=model, batch_size=50)
    if len(remainder) != 0:
        total_count: int = 0
        failed_count: int = 0
        for batch in remainder:
            total_count += len(batch)
            logger.debug("Saving %s item(s) one-by-one...", len(batch))
            failed_count += save_one_by_one(items=batch, model=model)
        logger.debug(
            "Saved %s out of the remaining %s item(s). %s",
            total_count-failed_count, total_count,
            f"Unable to add {failed_count} item(s), ignoring...")


def save_store_results(results: Sequence[schemas.Store]) -> None:
    """Save store results to the database.

    Intended to be used as a FastAPI background task.

    Args:
        results (Sequence[schemas.Store]):
            The parsed store results to be saved.
    """
    logger.debug("Running background task to save store results...")
    save_items(items=results, model=models.Store)


def save_product_results(results: ProductSearchResultT) -> None:
    """Save product results to the database.

    Intended to be used as a FastAPI background task.

    Args:
        results (ProductSearchResultT):
            The parsed product results to be saved.
    """
    logger.debug("Running background task to save product results...")
    products: list[schemas.Product] = []
    product_data: list[dict[str, str | int]] = []
    for result in results:
        for item in result[1]:  # Accessing the result tuple
            products.append(item[0])  # item[0] type: schemas.Product
            data = dict(item[1])  # Convert to dict
            data["store_id"] = int(result[0]["store_id"])
            data["product_ean"] = str(item[0].ean)
            product_data.append(data)

    # Save the Product(s) first
    save_items(items=products, model=models.Product)

    # Save the ProductData second
    save_items(items=product_data, model=models.ProductData)
