"""Contains CRUD operations for interaction with the database."""
from typing import Type, TypeVar, Any
from sqlalchemy import insert as sql_insert
from sqlalchemy.sql import Select

from app.core.typedefs import SchemaOut, OrmModel
from app.core.orm.database import SessionContext, Base
from app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)

ModelT = TypeVar("ModelT", bound=OrmModel)
SchemaT = TypeVar("SchemaT", bound=SchemaOut)


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
        table: Type[Base], records: list[dict[Any, Any]],
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
        session_ctx.session.commit()
        logger.debug(
            "Added %s records to the database as a bulk insert.",
            len(records))
        return True
    return False


def read_one(stmt: Select, session_ctx: SessionContext) -> OrmModel | None:
    """Read a single record from the database.

    Args:
        stmt (Select):
            The select statement to execute.
        session_ctx (SessionContext):
            The context manager for handling the database access.

    Returns:
        OrmModel | None:
            Returns an SQLAlchemy model bound to OrmModel. Returns
            None instead if no result was found or if an exception occurred.
    """
    with session_ctx:
        return session_ctx.session.scalars(stmt).one_or_none()
    return None


def read_all(stmt: Select, session_ctx: SessionContext) -> list[OrmModel]:
    """Read multiple records from the database.

    Args:
        stmt (Select):
            The select statement to execute.
        session_ctx (SessionContext):
            The context manager for handling the database access.

    Returns:
        list[OrmModel]:
            Returns a list of SQLAlchemy models bound to OrmModel. List may
            be empty if no results were found or if an exception occurred.
    """
    with session_ctx:
        return session_ctx.session.scalars(stmt).all()
    return []
