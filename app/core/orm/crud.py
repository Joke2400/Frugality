"""Contains CRUD operations for interaction with the database."""
from typing import Type, Sequence
from sqlalchemy import select, insert
from sqlalchemy.sql import Select
from app.core.orm import models, schemas, database
from app.utils import LoggerManager

from app.core.typedefs import (
    OrmModel,
    SchemaOut,
    SchemaInOrDict
)

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)

# TODO: Implement asynchronous database operations

# ---- GENERAL CREATION FUNCTIONS ----


def create_record(record: SchemaInOrDict, model: Type[OrmModel]) -> bool:
    """Add a new record to the database.

    Args:
        record (SchemaInOrDict):
            A Pydantic Schema (IN type only, see typedefs.py) or a dict.
        model (Type[OrmModelT]):
            The type for an ORM model defined in models.py

    Returns:
        bool:
            Returns True if the operation was successful.
            If an SQLAlchemy error was raised, or any other exception
            occurred inside the context (DBContext), returns False.
    """
    if not isinstance(record, dict):
        db_model: OrmModel = model(**dict(record))
    with database.DBContext() as context:
        logger.debug(
            "Adding a single '%s' record to the database...",
            record.__class__.__name__)
        context.session.add(db_model)
    if context.status is database.CommitState.SUCCESS:
        return True
    logger.debug(
        "Unable to add record %s (%s) to the database.",
        model, record.__class__.__name__)
    return False


def bulk_create_records(
        records: Sequence[SchemaInOrDict],
        model: Type[OrmModel]) -> bool:
    """Add records to the database using a bulk insert.

    Args:
        records (list[SchemaInOrDict]):
        The batch of items to be added to the database.
        Items must be Pydantic Schemas (IN type only, see typedefs.py).
        Alternatively dicts may also be passed

    Returns:
        bool:
        A boolean indicating if the operation was successful.
    """
    if not isinstance(records[0], dict):
        items: list[dict] = [dict(i) for i in records]  # Convert to dicts
    else:
        # Assuming the entire Sequence is a list of dicts
        items = records  # type: ignore
    with database.DBContext() as context:
        logger.debug(
            "Adding batch of %s '%s' records records to the database...",
            len(items), records[0].__class__.__name__)
        context.session.execute(
            insert(model),
            [*items]  # Unpack dicts into statement
        )
    if context.status is database.CommitState.SUCCESS:
        return True
    logger.debug(
        "Unable to add batch of records (%s) to the database.",
        records[0].__class__.__name__)
    return False


# ---- GENERAL READING FUNCTIONS ----

def select_one[SchemaT: SchemaOut](
        stmt: Select, cast: Type[SchemaT]
        ) -> SchemaT | None:
    """Get a single item from the database using the given select query.

    The resulting ORM-object is casted to the specified
    Pydantic schema before being returned from the function.

    Args:
        stmt (Select):
            A previously constructed SQLAlchemy Select object.
            This is used in the call to session.scalars.
        cast (Type[SchemaOut]):
            The type of the Pydantic schema to cast the result to.
            The upper bound is defined by SchemaOut (see typedefs).

    Returns:
        SchemaOut | None:
            The validated instance of the given SchemaT type.
            Returns None if the item could not be retrieved.
    """
    result: SchemaT | None = None
    with database.DBContext(read_only=True) as context:
        item: OrmModel | None = context.session.scalars(stmt).one_or_none()
        if item is not None:
            result = cast.model_validate(item)
    return result


def select_all[SchemaT: SchemaOut](
        stmt: Select, cast: Type[SchemaT]
        ) -> list[SchemaT]:
    """Get a list of items from the database using the given select query.

    The resulting ORM-objects are casted to the specified
    Pydantic schema before being returned from the function.

    Args:
        stmt (Select):
            A previously constructed SQLAlchemy Select object.
            This is used in the call to session.scalars.
        cast (Type[SchemaT]):
            The type of the Pydantic schema to cast the results to.
            The upper bound is defined by SchemaOut (see typedefs).

    Returns:
        list[SchemaT]:
            A list of validated instances of the given SchemaT type.
            The list may be empty if no items could be retrieved.
    """
    result: list[SchemaT] = []
    with database.DBContext(read_only=True) as context:
        items: list[OrmModel] = context.session.scalars(stmt).all()
        result = [
            cast.model_validate(item) for item in items
        ]
    return result


# ---- STORE GET FUNCTIONS ----


def get_store_by_id(store_id: int) -> schemas.StoreDB | None:
    """Get a store by id."""
    stmt = (
        select(models.Store)
        .where(models.Store.store_id == store_id)
    )
    return select_one(stmt=stmt, cast=schemas.StoreDB)


def get_store_by_slug(slug: str) -> schemas.StoreDB | None:
    """Get a store by slug."""
    stmt = (
        select(models.Store)
        .where(models.Store.slug == slug)
    )
    return select_one(stmt=stmt, cast=schemas.StoreDB)


def get_stores_by_name(
        name: str, brand: str | None = None) -> list[schemas.StoreDB]:
    """Get stores by name."""
    stmt = (
        select(models.Store)
        .where(models.Store.store_name.ilike(
            f"%{name}%"))
    )
    if brand is not None:
        stmt = stmt.where(models.Store.brand == brand)
    stmt = stmt.order_by(models.Store.store_name)
    return select_all(stmt=stmt, cast=schemas.StoreDB)

# ---- PRODUCT GET FUNCTIONS ----


def get_product_by_ean(ean: str) -> schemas.ProductDB | None:
    """Get a store by ean."""
    stmt = (
        select(models.Product)
        .where(models.Product.ean == ean)
    )
    return select_one(stmt=stmt, cast=schemas.ProductDB)


def get_product_by_slug(slug: str) -> schemas.ProductDB | None:
    """Get a product by slug."""
    stmt = (
        select(models.Product)
        .where(models.Product.slug == slug)
    )
    return select_one(stmt=stmt, cast=schemas.ProductDB)


def get_products_by_name(
        name: str, category: str | None = None) -> list[schemas.ProductDB]:
    """Get products by name."""
    stmt = (
        select(models.Product)
        .where(models.Product.name.ilike(
            f"%{name}%"
        ))
    )
    if category is not None:
        stmt = stmt.where(models.Product.category == category)
    stmt = stmt.order_by(models.Product.name)
    return select_all(stmt=stmt, cast=schemas.ProductDB)
