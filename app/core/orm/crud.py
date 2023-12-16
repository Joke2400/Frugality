"""Contains CRUD operations for interaction with the database."""
from typing import TypeVar
from sqlalchemy import select, insert
from app.core.orm import models, schemas, database
from app.core import parse
from app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


# TODO: Implement asynchronous database operations
# TODO: Batched/bulk commits on products / stores

SchemasAlias = schemas.Store | schemas.Product | schemas.ProductData
ModelsAlias = models.Store | models.Product | models.ProductData
PydanticSchemaT = TypeVar("PydanticSchemaT", bound=SchemasAlias)
OrmModelT = TypeVar("OrmModelT", bound=ModelsAlias)


def add_store_record(store: schemas.Store) -> bool:
    """Add a new 'Store' record to the database (CRUD).

    Uses an EAFP approach -> attempts to add the store ->
    if an error is raised -> the transaction gets rolled back.

    Args:
        store (schemas.Store):
        A pydantic Store instance.

    Returns:
        bool:
        A boolean indicating if the operation was successful.
    """
    db_store = models.Store(**dict(store))
    with database.DBContext() as context:
        logger.debug(
            "Adding store record: ('%s', %s) to database...",
            db_store.store_name, db_store.store_id)
        context.session.add(db_store)
    if context.status is database.CommitState.SUCCESS:
        return True
    logger.debug(
        "Unable to add store record: ('%s', %s) to database.",
        store.store_name, store.store_id)
    return False


def add_product_record(product: schemas.Product) -> bool:
    """Add a new 'Product' record to the database (CRUD).

    Uses an EAFP approach -> attempts to add the product ->
    if an error is raised -> the transaction gets rolled back.

    Args:
        product (schemas.Product):
        A pydantic Product instance.

    Returns:
        bool:
        A boolean indicating if the operation was successful.
    """
    db_product = models.Product(**dict(product))
    with database.DBContext() as context:
        logger.debug(
            "Adding product record: ('%s', '%s) to database...",
            product.name, product.ean)
        context.session.add(db_product)
    if context.status is database.CommitState.SUCCESS:
        return True
    logger.debug(
        "Unable to add product record: ('%s', '%s') to database.",
        product.name, product.ean)
    return False


def add_product_data_record(product_data: schemas.ProductData) -> bool:
    db_product_data = models.ProductData(**dict(product_data))
    with database.DBContext() as context:
        context.session.add(db_product_data)
    if context.status is database.CommitState.SUCCESS:
        logger.debug(
            "Added product data record for: \
            (store_id: %s, product_ean: %s) to database.")
        return True
    logger.debug(
        "Unable to add product data record for: \
        (store_id: %s, product_ean: %s) to database.")
    return False


def bulk_add_records(records: list[PydanticSchemaT], model: OrmModelT) -> bool:
    """Add records to the database using a bulk insert.

    Args:
        records (list[PydanticSchemaT]):
        The batch of items to be added to the database.

    Returns:
        bool:
        A boolean indicating if the operation was successful.
    """
    items = [dict(i) for i in records]  # Convert the schemas to dicts
    with database.DBContext() as context:
        logger.debug(
            "Adding batch of %s '%s' records to database...",
            len(items), records[0])
        context.session.execute(
            insert(model),
            [*items]  # Unpack dicts into statement
        )
    if context.status is database.CommitState.SUCCESS:
        return True
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
