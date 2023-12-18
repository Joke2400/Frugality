"""Contains CRUD operations for interaction with the database."""
from typing import Type, Sequence
from sqlalchemy import select, insert
from app.core import parse
from app.core.orm import models, schemas, database
from app.utils import LoggerManager

from app.core.typedefs import (
    PydanticSchemaInT,
    OrmModelT
)

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)
# TODO: Implement asynchronous database operations


def create_record(record: PydanticSchemaInT, model: Type[OrmModelT]) -> bool:
    """Add a new record to the database.


    Args:
        record (PydanticSchemaT):
            An instance of a Pydantic schema defined in schemas.py
        model (Type[OrmModelT]):
            The type for an ORM model defined in models.py

    Returns:
        bool:
            Returns True if the operation was successful.
            If an SQLAlchemy error was raised, or any other exception
            occurred inside the context (DBContext), returns False.
    """
    db_model: OrmModelT = model(**dict(record))
    with database.DBContext() as context:
        logger.debug(
            "Adding a single (%s) record to the database...",
            type(model))
        context.session.add(db_model)
    if context.status is database.CommitState.SUCCESS:
        return True
    logger.debug(
        "Unable to add record %s of type [%s] to the database.",
        model, type(model))
    return False


def bulk_create_records(
        records: Sequence[PydanticSchemaInT], model: Type[OrmModelT]) -> bool:
    """Add records to the database using a bulk insert.

    Args:
        records (list[PydanticSchemaT]):
        The batch of items to be added to the database.

    Returns:
        bool:
        A boolean indicating if the operation was successful.
    """
    items: list[dict] = [dict(i) for i in records]  # Convert to dicts
    with database.DBContext() as context:
        logger.debug(
            "Adding batch of %s (%s) records records to the database...",
            len(items), type(records[0]))
        context.session.execute(
            insert(model),
            [*items]  # Unpack dicts into statement
        )
    if context.status is database.CommitState.SUCCESS:
        return True
    logger.debug(
        "Unable to add batch of records of type [%s] to the database.",
        type(items[0]))
    return False


def get_product_by_ean(ean: str) -> schemas.ProductDB | None:
    """Get Product records by product EAN (CRUD).

    Pattern: WHERE models.Product.ean = ean

    Args:
        ean (str): Product EAN to query using.

    Returns:
        schemas.ProductDB | None:
        A pydantic ProductDB instance or None if not found.
    """
    with database.DBContext() as context:
        session = context.session
        stmt = (
            select(models.Product)
            .where(models.Product.ean == ean)
        )
        logger.debug("Fetching product by ean... (%s)", ean)
        product = session.scalars(stmt).one_or_none()
        if product is None:
            return None
        result: schemas.ProductDB = schemas.ProductDB.model_validate(product)
    return result


def get_store_by_id(store_id: int) -> schemas.StoreDB | None:
    """Get Store records by store id (CRUD).

    Pattern: WHERE models.Store.store_id = store_id

    Args:
        store_id (int): Store id to query using.

    Returns:
        schemas.StoreDB | None:
        A pydantic StoreDB instance or None if not found.
    """
    with database.DBContext(read_only=True) as context:
        session = context.session
        stmt = (
            select(models.Store)
            .where(models.Store.store_id == store_id)
        )
        logger.debug("Fetching store by id... (%s)", store_id)
        store = session.scalars(stmt).one_or_none()
        if store is None:
            return None
        result: schemas.StoreDB = schemas.StoreDB.model_validate(store)
    return result


def get_stores_by_slug(query: str) -> list[schemas.StoreDB]:
    """Get Store records by store slug (CRUD).

    Parses the given string into an item slug before a query.

    Implements SQL LIKE operator on the parsed slug ->
        pattern: WHERE slug LIKE %slug%

    If a brand is present at the start of the string ->
        pattern: WHERE slug LIKE %slug% AND brand = brand

    Args:
        query (str):
        The entire query string, may include store brand at start.

    Returns:
        list[schemas.StoreDB]:
        A list of pydantic StoreDB instances.
        The list may be empty if no results were found.
    """
    brand = parse.parse_store_brand_from_string(query)
    with database.DBContext(read_only=True) as context:
        session = context.session
        slug_query = parse.slugify(query)
        stmt = (
            select(models.Store)
            .where(models.Store.slug.like(f"%{slug_query}%"))
            )
        if brand is not None:
            stmt = stmt.where(models.Store.brand == brand)
            logger.debug(
                "Fetching stores by slug... (brand=%s, query=%s)",
                brand, slug_query)
        else:
            logger.debug(
                "Fetching stores by slug... (query=%s)",
                slug_query)
        stmt = stmt.order_by(models.Store.store_name)
        stores = session.scalars(stmt).all()
        result: list[schemas.StoreDB] = [
            schemas.StoreDB.model_validate(i) for i in stores
        ]
    return result


def get_stores() -> list[schemas.StoreDB]:
    """Get all Store records (CRUD).

    Returns:
        list[schemas.StoreDB]:
        A list of pydantic StoreDB instances.
        The list may be empty if no stores exist in the table.
    """
    with database.DBContext(read_only=True) as context:
        session = context.session
        logger.debug("Fetching all stores from db...")
        stores = session.scalars(select(models.Store)).all()
        result: list[schemas.StoreDB] = [
            schemas.StoreDB.model_validate(i) for i in stores
        ]
    return result
