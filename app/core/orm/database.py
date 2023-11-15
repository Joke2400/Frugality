"""Contains a database context manager."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase

from app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=20, fh=10)


class Base(DeclarativeBase):
    """Base for SQLAlchemy models."""


class DBContext:
    """Context manager for managing database sessions."""

    session: Session
    engine: Engine
    _sessionmaker: sessionmaker

    @classmethod
    def prepare_context(cls, url: str, purge_all_tables: bool = False):
        """
        Create engine and sessionmaker, call create_all().

        Must be called once before context manager is used.
        """
        cls.engine = create_engine(url=url)
        cls._sessionmaker = sessionmaker(bind=cls.engine)
        if purge_all_tables:
            Base.metadata.drop_all(bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)
        logger.debug("Configured DBContext.")

    def __enter__(self) -> Session:
        """Create a session and return it."""
        self.session = self._sessionmaker()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit context & commit changes"""
        try:
            if exc_type is None:
                self.session.commit()
                logger.debug("Committed the database transaction.")
            else:
                self.session.rollback()
                logger.debug("Rolled back the database transaction.")
        except SQLAlchemyError as err:  # THIS ERROR IS TOO GENERIC; CHANGE LATER
            logger.exception(err)
            self.session.rollback()
        finally:
            self.session.close()
            logger.debug("Closed the database session.")
