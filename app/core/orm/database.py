"""Contains a database context manager."""
from enum import Enum
from typing_extensions import Self
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
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
            "[Session ID: %s] Opened a database session.",
            self.session.hash_key)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Exit context & commit changes"""
        if exc_type is not None:
            logger.debug(exc_value)
            self.session.rollback()
            self.status = CommitState.FAIL
            logger.debug(
                "[Session ID: %s] Performed a rollback due to an error.",
                self.session.hash_key)
            return True
        try:
            if not self.read_only:
                self.session.commit()
        except SQLAlchemyError as err:
            logger.debug(err)
        else:
            # If no error was raised:
            self.status = CommitState.SUCCESS
            logger.debug(
                "[Session ID: %s] Committed the database transaction.",
                self.session.hash_key)
            self.session.close()
            logger.debug(
                "[Session ID: %s] Closed the database session.",
                self.session.hash_key)
            return True

        # If an error was raised:
        self.session.rollback()
        self.status = CommitState.FAIL
        logger.debug(
            "[Session ID: %s] Performed a rollback due to an error.",
            self.session.hash_key)
        self.session.close()
        logger.debug(
            "[Session ID: %s] Closed the database session.",
            self.session.hash_key)
        return True
