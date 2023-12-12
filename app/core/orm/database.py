"""Contains a database context manager."""
from enum import Enum
from typing import Self
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase

from app.utils import LoggerManager


logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


class Base(DeclarativeBase):
    """Base for SQLAlchemy models."""
    # Defining this here, gets used in core.orm.models


class CommitState(str, Enum):
    """Enumeration for representing the state of a db commit.

    Values:
        SUCCESS  |  FAIL  |  PENDING
    """
    # TODO Reassess: 'this' vs just using a boolean value
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    PENDING = "PENDING"


class DBContext:
    """Context manager for managing database sessions."""

    status: CommitState
    session: Session
    _engine: Engine
    _sessionmaker: sessionmaker
    read_only: bool

    @classmethod
    def prepare_context(cls, url: str, purge_all_tables: bool = False):
        """
        Create engine and sessionmaker, call create_all().

        Must be called before the context manager is used for the first time.
        """
        cls._engine = create_engine(url=url)
        cls._sessionmaker = sessionmaker(bind=cls._engine)

        # TODO: Add a separate check to prompt the user if in prod,
        # so that no data gets accidentally deleted
        if purge_all_tables:
            Base.metadata.drop_all(bind=cls._engine)
            logger.debug(
                "Purged all database tables. purge_all_tables was set to True")
        Base.metadata.create_all(bind=cls._engine)
        logger.debug("STARTUP: Successfully prepared the database context.")

    def __init__(self, read_only: bool = False):
        self.read_only = read_only

    def __enter__(self) -> Self:
        """Create a session and return it."""
        self.session: Session = self._sessionmaker()
        self.status = CommitState.PENDING
        logger.debug(
            "ID: %s Opened a new database session.",
            self.session.hash_key)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit context & commit changes"""
        try:
            if exc_type is None:
                if not self.read_only:
                    self.session.commit()
                    self.status = CommitState.SUCCESS
                    logger.debug(
                        "Successfully committed a database transaction.")
            else:
                self.session.rollback()
                self.status = CommitState.FAIL
                logger.debug(
                    "Performed a transaction rollback due to an error.")
        except SQLAlchemyError as err:
            self.session.rollback()
            self.status = CommitState.FAIL
            logger.debug(
                "Performed a transaction rollback due to an error.")
            logger.debug(err)
        finally:
            self.session.close()
            logger.debug(
                "ID: %s Closed the database session.",
                self.session.hash_key)
