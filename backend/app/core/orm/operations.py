"""Contains operations for fetching (& converting) data from db."""
from sqlalchemy import select
from pydantic import ValidationError
from app.core.orm import models, schemas, crud, database
from app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


def get_store_by_id(store_id: int) -> schemas.StoreDB | None:
    """Get a single store from the database by its ID."""
    item: schemas.StoreDB | None = None
    stmt = (
        select(models.Store)
        .where(models.Store.store_id == store_id)
    )
    ctx = database.ORM().get_session_context(close_on_exit=False)
    result = crud.read_one(stmt=stmt, session_ctx=ctx)
    try:
        if result is not None:
            item = schemas.StoreDB.model_validate(result)
    except ValidationError as err:
        logger.debug(err)
    ctx.session.close()
    return item


def get_stores_by_name(
        name: str, brand: str | None = None) -> list[schemas.StoreDB]:
    """Get multiple stores from the database by searching by name."""
    items: list[schemas.StoreDB] = []
    stmt = (
        select(models.Store)
        .where(models.Store.store_name.ilike(
            f"%{name}%"))
    )
    if brand is not None:
        stmt = stmt.where(models.Store.brand == brand)
    stmt = stmt.order_by(models.Store.store_name)
    ctx = database.ORM().get_session_context(close_on_exit=False)
    result = crud.read_all(stmt=stmt, session_ctx=ctx)
    try:
        if len(result) > 0:
            items = [schemas.StoreDB.model_validate(i) for i in result]
    except ValidationError as err:
        logger.debug(err)
    ctx.session.close()
    return items


def get_product_by_ean(ean: str) -> schemas.ProductDB | None:
    """Get a single product from the database by its EAN."""
    item: schemas.ProductDB | None = None
    stmt = (
        select(models.Product)
        .where(models.Product.ean == ean)
    )
    ctx = database.ORM().get_session_context(close_on_exit=False)
    result = crud.read_one(stmt=stmt, session_ctx=ctx)
    try:
        if result is not None:
            item = schemas.ProductDB.model_validate(result)
    except ValidationError as err:
        logger.debug(err)
    ctx.session.close()
    return item


def get_products_by_name(
        name: str, category: str | None = None) -> list[schemas.ProductDB]:
    """Get multiple products from the database by searching by name."""
    items: list[schemas.ProductDB] = []
    stmt = (
        select(models.Product)
        .where(models.Product.name.ilike(
            f"%{name}%"
        ))
    )
    if category is not None:
        stmt = stmt.where(models.Product.category == category)
    stmt = stmt.order_by(models.Product.name)
    ctx = database.ORM().get_session_context(close_on_exit=False)
    result = crud.read_all(stmt=stmt, session_ctx=ctx)
    try:
        if len(result) > 0:
            items = [schemas.ProductDB.model_validate(i) for i in result]
    except ValidationError as err:
        logger.debug(err)
    ctx.session.close()
    return items
