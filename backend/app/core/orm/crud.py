"""Contains CRUD operations for interaction with the database."""
from typing import Type, TypeVar
from sqlalchemy import select, insert as sql_insert
from sqlalchemy.sql import Select

from backend.app.core.typedefs import SchemaOut, OrmModel
from backend.app.core.orm.database import SessionContext, Base
from backend.app.utils import LoggerManager

from . import models
from . import schemas

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)

ModelT = TypeVar("ModelT", bound=OrmModel)


def create(record: ModelT, session_ctx: SessionContext) -> ModelT | None:
    """Create a new database record using the given model.

    Args:
        record (ModelT):
            The SQLAlchemy model for the record to be created.
        session_ctx (SessionContext):
            The context manager for handling the database access.

    Returns:
        ModelT | None:
            Returns the same record when successful and None upon fail.
    """
    with session_ctx:
        session_ctx.session.add(record)
        session_ctx.session.commit()
        logger.debug("Added a single record to the database.")
        return record
    return None


def insert(
        table: Type[Base], records: list[dict],
        session_ctx: SessionContext) -> bool:
    """Create multiple new database records from the given list.

    Args:
        record (ModelT):
            The list of item-dicts to be inserted into the database.
        session_ctx (SessionContext):
            The context manager for handling the database access.

    Returns:
        bool:
            Returns True if the insert is successful, False if not.
    """
    with session_ctx:
        session_ctx.session.execute(
            sql_insert(table),  # Model type is fetched from first element
            [*records]
        )
        logger.debug(
            "Added %s records to the database as a bulk insert.",
            len(records))
        return True
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


def select_all_join[SchemaT: SchemaOut](
        stmt: Select,
        table_cast: Type[SchemaT],
        join_cast: Type[SchemaT],
        ) -> tuple[SchemaT, SchemaT]:
    result: list[tuple[SchemaT, SchemaT]] = []
    with database.DBContext(read_only=True) as context:
        print(len(context.session.execute(stmt).all()))
    return None

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
