"""Contains CRUD operations for interaction with the database."""
from sqlalchemy import select
from app.core.orm import models, schemas, database
from app.core import parse


def create_store(store: schemas.Store) -> None:
    """CRUD: Create a new Store record.

    Args:
        store (schemas.Store):
        Takes in a pydantic Store instance.
    """
    with database.DBContext() as session:
        db_store = models.Store(**dict(store))
        session.add(db_store)


def create_product(product: schemas.Product,
                   data: schemas.ProductData) -> None:
    # TODO: Add check: if product exists
    with database.DBContext() as session:
        db_product = models.Product(
            **dict(product))
        db_product_data = models.ProductData(
            **dict(data))
        session.add(db_product)
        db_product.data.append(db_product_data)


def get_product_by_ean(ean: str) -> schemas.ProductDB | None:
    """CRUD: Get Product records by product EAN.

    Pattern: WHERE models.Product.ean = ean

    Args:
        ean (str): Product EAN to query using.

    Returns:
        schemas.ProductDB | None:
        A pydantic ProductDB instance or None if not found.
    """
    with database.DBContext() as session:
        stmt = (
            select(models.Product)
            .where(models.Product.ean == ean)
        )
        product = session.scalars(stmt).one_or_none()
        if product is None:
            return None
        return schemas.ProductDB.model_validate(product)


def get_store_by_id(query: int) -> schemas.StoreDB | None:
    """CRUD: Get Store records by store id.

    Pattern: WHERE models.Store.store_id = query

    Args:
        query (int): Store id to query using.

    Returns:
        schemas.StoreDB | None:
        A pydantic StoreDB instance or None if not found.
    """
    with database.DBContext() as session:
        stmt = (
            select(models.Store)
            .where(models.Store.store_id == query)
        )
        store = session.scalars(stmt).one_or_none()
        if store is None:
            return None
        return schemas.StoreDB.model_validate(store)


def get_stores_by_slug(query: str) -> list[schemas.StoreDB]:
    """CRUD: Get Store records by store slug.

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
    with database.DBContext() as session:
        stmt = (
            select(models.Store)
            .where(models.Store.slug.like(f"%{parse.slugify(query)}%"))
            )
        if brand is not None:
            query = query.lstrip(brand.capitalize()).strip()
            stmt = stmt.where(models.Store.brand == brand)

        stmt = stmt.order_by(models.Store.store_name)
        stores = session.scalars(stmt).all()
        return [schemas.StoreDB.model_validate(i) for i in stores]


def get_stores() -> list[schemas.StoreDB]:
    """CRUD: Get all Store records.

    Returns:
        list[schemas.StoreDB]:
        A list of pydantic StoreDB instances.
        The list may be empty if no stores exist in the table.
    """
    with database.DBContext() as session:
        stores = session.scalars(select(models.Store)).all()
        return [schemas.StoreDB.model_validate(i) for i in stores]
