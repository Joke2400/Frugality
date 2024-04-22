"""Contains a database context manager."""
from typing_extensions import Self
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.orm import DeclarativeBase

from backend.app.utils import patterns
from backend.app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


class Base(DeclarativeBase):
    """Base for SQLAlchemy models."""
    # Defining this here, gets used in core.orm.models


class SessionContext:
    """A context manager for handling database accesses.

    Performs logging tasks & handles any raised exceptions.
    Also handles database commits & rollbacks when exiting the context.
    """
    session: Session
    read_only: bool
    close_on_exit: bool
    prev_exc: Exception | None

    __slots__ = "session", "read_only", "close_on_exit", "prev_exc"

    def __init__(self, session: Session, read_only: bool,
                 close_on_exit: bool = True) -> None:
        self.session = session
        self.read_only = read_only
        self.close_on_exit = close_on_exit
        self.prev_exc = None

    def __enter__(self) -> Self:
        logger.debug(
            "[SESSION_ID: %s] Entered the session context.",
            self.session.hash_key)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_type is None:
            self.prev_exc = None
            if self.close_on_exit:
                self.session.close()
            return True
        self.session.rollback()
        self.prev_exc = exc_type
        logger.debug(
            "[SESSION_ID: %s] Transaction raised an %s %s",
            self.session.hash_key, exc_type.__name__, exc_value)
        self.session.close()
        if exc_type in (IntegrityError, DataError):
            return True
        return False


class ORM(metaclass=patterns.SingletonMeta):
    """An internal abstraction of the SQLAlchemy ORM.

    Creates the ORM engine & handles the creation/deletion of tables.
    Provides SessionContext-instances for use in database access.

    The class is a Singleton, so successive calls to will yield
    the same instance of this class as the first call.

    NOTE that the initial call must provide a value for the
    connect url; so that the SQLAlchemy Engine can be created.
    """
    _engine: Engine
    _sessionmaker: sessionmaker

    __slots__ = "_engine", "_sessionmaker"

    def __init__(self, url: str = "", purge: bool = False) -> None:
        if url == "":
            raise ValueError(
                "URL must be provided upon first call to ORM __init__")
        self._engine = create_engine(url=url)
        self._sessionmaker = sessionmaker(bind=self._engine)
        if purge:
            self.purge_all()
        self.create_all()
        logger.info("SQLAlchemy ORM is now operational.")

    def create_all(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self._engine)
        logger.debug("ORM: Created all database tables.")

    def purge_all(self) -> None:
        """Purge all database tables."""
        Base.metadata.drop_all(bind=self._engine)
        logger.debug("ORM: Purged all database tables.")

    def get_session_context(
            self, read_only: bool,
            close_on_exit: bool = True) -> SessionContext:
        """Get a session context with a new session within."""
        return SessionContext(
            session=self._sessionmaker(),
            read_only=read_only,
            close_on_exit=close_on_exit)
