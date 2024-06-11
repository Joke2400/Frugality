"""Contains operations for fetching (& converting) data from db."""
from datetime import datetime, timedelta
from sqlalchemy import select, and_, join
from pydantic import ValidationError
from app.core.typedefs import StoreDB, ProductDB
from app.core.orm import models, schemas, crud, database
from app.core import parse
from app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


def get_store_by_id(store_id: int) -> StoreDB | None:
    """Get a single store from the database by its ID."""
    item: StoreDB | None = None
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
        name: str, brand: str | None = None) -> list[StoreDB]:
    """Get multiple stores from the database by searching by name."""
    items: list[StoreDB] = []
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


def get_product_by_ean(ean: str) -> ProductDB | None:
    """Get a single product from the database by its EAN."""
    item: ProductDB | None = None
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
        name: str, category: str | None = None) -> list[ProductDB]:
    """Get multiple products from the database by searching by name."""
    items: list[ProductDB] = []
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


def get_recent_complete_product_records(
        query: str, store_ids: list[int], timedelta_hours: int
        ) -> list[tuple[ProductDB, schemas.ProductDataDB]]:
    """TODO: Needs improvement & tests"""
    items: list[tuple[ProductDB, schemas.ProductDataDB]] = []
    time_offset = datetime.now() - timedelta(hours=timedelta_hours)
    stmt = (
        select(
            models.Product, models.ProductData)
        .select_from(
            join(
                models.Product, models.ProductData,
                models.Product.ean == models.ProductData.ean))
        .where(
            and_(
                models.Product.slug.like(f"%{parse.slugify(query)}%"),
                models.ProductData.timestamp >= time_offset,
                models.ProductData.store_id.in_([*store_ids])
            )
        )
    )
    ctx = database.ORM().get_session_context(close_on_exit=False)
    result = ctx.session.execute(stmt).all()
    try:
        if len(result) > 0:
            for p, d in result:
                validated = (
                    # Pylance is unhappy without the [] below
                    schemas.ProductDB[schemas.ProductDataDB].model_validate(p),
                    schemas.ProductDataDB.model_validate(d))
                items.append(validated)
    except ValidationError as err:
        logger.debug(err)
    ctx.session.close()
    return items
