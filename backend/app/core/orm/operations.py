from typing import Type
from sqlalchemy import select
from pydantic import ValidationError
from backend.app.core.orm.database import SessionContext
from backend.app.core.orm import models, schemas, crud, database
from backend.app.core.typedefs import SchemaOut, SchemaIn, OrmModel
from backend.app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


def get_store_by_id(store_id: int) -> schemas.StoreDB | None:
    stmt = (
        select(models.Store)
        .where(models.Store.store_id == store_id)
    )
    ctx = database.ORM().get_session_context()
    result = crud.read_one(stmt=stmt, session_ctx=ctx)
    try:
        return schemas.StoreDB.model_validate(result)
    except ValidationError as err:
        logger.debug(err)
    return None


def get_stores_by_name(name: str, brand: str) -> list[schemas.StoreDB]:
    stmt = (
        select(models.Store)
        .where(models.Store.store_name.ilike(
            f"%{name}%"))
    )
    if brand is not None:
        stmt = stmt.where(models.Store.brand == brand)
    stmt = stmt.order_by(models.Store.store_name)
    ctx = database.ORM().get_session_context()
    result = crud.read_all(stmt=stmt, session_ctx=ctx)
    try:
        return [schemas.StoreDB.model_validate(i) for i in result]
    except ValidationError as err:
        logger.debug(err)
    return []


def get_product_by_ean(ean: str) -> schemas.ProductDB | None:
    stmt = (
        select(models.Product)
        .where(models.Product.ean == ean)
    )
    ctx = database.ORM().get_session_context()
    result = crud.read_one(stmt=stmt, session_ctx=ctx)
    try:
        return schemas.ProductDB.model_validate(result)
    except ValidationError as err:
        logger.debug(err)
    return None


def get_products_by_name(name: str, category: str) -> list[schemas.ProductDB]:
    stmt = (
        select(models.Product)
        .where(models.Product.name.ilike(
            f"%{name}%"
        ))
    )
    if category is not None:
        stmt = stmt.where(models.Product.category == category)
    stmt = stmt.order_by(models.Product.name)
    ctx = database.ORM().get_session_context()
    result = crud.read_all(stmt=stmt, session_ctx=ctx)
    try:
        return [schemas.ProductDB.model_validate(i) for i in result]
    except ValidationError as err:
        logger.debug(err)
    return []
