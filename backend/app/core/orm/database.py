"""Contains a database context manager."""
from enum import Enum
from typing_extensions import Self
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import DeclarativeBase

from backend.app.utils import LoggerManager
from backend.app.utils.exceptions import ExceptionInContext

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
    def prepare_context(
            cls, url: str,
            purge: bool = False):
        """
        Create engine and sessionmaker, call create_all().

        Must be called before the context manager is used for the first time.
        """
        cls._engine = create_engine(url=url, pool_pre_ping=True)
        cls._sessionmaker = sessionmaker(bind=cls._engine)

        if purge:
            Base.metadata.drop_all(bind=cls._engine)
            logger.info(
                "Purged the existing database tables. purge was set to True")
        Base.metadata.create_all(bind=cls._engine)
        logger.info("Database context manager was successfully prepared.")

    def __init__(self, read_only: bool = False):
        self.read_only = read_only

    def __enter__(self) -> Self:
        """Create a session and return it."""
        self.session: Session = self._sessionmaker()
        self.status = CommitState.PENDING
        logger.debug(
            "[ID: %s] Opened the database session.",
            self.session.hash_key)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Commit or rollback changes, close the session."""
        # Set status to FAIL, must thus be explicitly set later on
        self.status = CommitState.FAIL
        propagate_exc = False  # <-- Only relevant if an exception occurred
        try:
            # Check if an exception occurred within the context
            if exc_type is None:
                if not self.read_only:
                    self.session.commit()
            else:
                # An IntegrityError within context is re-raised
                if exc_type is IntegrityError:
                    raise exc_value
                # All other "unknown" exceptions propagate further
                raise ExceptionInContext(exc_value)
        except IntegrityError as err:
            logger.debug(
                "[ID: %s] Transaction raised an IntegrityError %s",
                self.session.hash_key, err)
        except SQLAlchemyError as err:
            logger.exception(
                "[ID: %s] Transaction raised an error: %s",
                self.session.hash_key, err)
        except ExceptionInContext as err:
            logger.debug(err)
            propagate_exc = True
        else:
            # As no exception occurred -> set status to SUCCESS
            self.status = CommitState.SUCCESS
            if not self.read_only:
                logger.debug(
                    "[ID: %s] Transaction successfully committed.",
                    self.session.hash_key)
        # Perform rollback as commit was not successful
        if self.status is CommitState.FAIL:
            self.session.rollback()
            logger.debug(
                "[ID: %s] Transaction was rolled back due to an error.",
                self.session.hash_key)
        self.session.close()
        logger.debug(
            "[ID: %s] Closed the database session.",
            self.session.hash_key)
        if self.status is not CommitState.SUCCESS:
            if propagate_exc:
                return False
        return True
