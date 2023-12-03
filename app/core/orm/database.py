"""Contains a database context manager."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import DeclarativeBase
from fastapi import HTTPException

from app.utils import LoggerManager


logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


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
        logger.debug("DBContext: Begun database transaction.")
        return self.session

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit context & commit changes"""
        try:
            if exc_type is None:
                self.session.commit()
                logger.debug("DBContext: Committed the database transaction.")
            else:
                self.session.rollback()
                logger.debug("DBContext: Rolled back the database transaction.")
        except IntegrityError as err:
            # Re-raising in order to handle elsewhere.
            # NOTE: Should maybe consider another solution in the future...
            # Raising http exception works since its called from a route,
            # But its very much unclear why HTTPException is called,
            # Need to just not catch the integrity error or just create
            # a custom error type for this.
            self.session.rollback()
            raise HTTPException(
                status_code=422, detail="Unable to add record.") from err

        except SQLAlchemyError as err:  # THIS ERROR IS TOO GENERIC; CHANGE LATER
            self.session.rollback()
            logger.exception(err)
        finally:
            self.session.close()
            logger.debug("Closed the database session.")


async def get_db() -> Session:
    """Create a context manager and yield a database session."""
    with DBContext() as session:
        yield session
