"""Contains a database context manager."""
from typing_extensions import Self
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    OperationalError,
    MultipleResultsFound
)
from backend.app.utils import patterns, LoggerManager

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


class Base(DeclarativeBase):
    """Base for SQLAlchemy models."""
    # Defining this here, gets used in core.orm.models


class SessionContext:
    """A context manager for handling database accesses.

    Performs logging tasks & handles any raised exceptions.
    Also handles database commits & rollbacks when exiting the context.

    Args:
        session (sqlalchemy.orm.Session):
            The SQLAlchemy session to bind to the context.
        close_on_exit (bool):
            Set this to False if the session should not be closed upon
            context manager __exit__() call. Defaults to True.
            NOTE that if this is set to False, you will have to
            manually close the Session after use.

    Fields:
        prev_exc (Exception | None):
            Holds the exception type of the previously occurred exception.
            Is set to None instead if the previous use of the context
            manager yielded no exception.
    """
    session: Session
    close_on_exit: bool
    prev_exc: Exception | None

    __slots__ = "session", "close_on_exit", "prev_exc"

    def __init__(self, session: Session,
                 close_on_exit: bool = True) -> None:
        self.session = session
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
            logger.debug(
                "[SESSION_ID: %s] Exited the session context.",
                self.session.hash_key)
            return True
        self.session.rollback()
        self.prev_exc = exc_type
        logger.debug(
            "[SESSION_ID: %s] Transaction raised an %s: %s",
            self.session.hash_key, exc_type.__name__, exc_value)
        self.session.close()
        logger.debug(
            "[SESSION_ID: %s] Exited the session context.",
            self.session.hash_key)
        if exc_type in (IntegrityError, DataError, MultipleResultsFound):
            return True
        return False


class ORM(metaclass=patterns.SingletonMeta):
    """An internal abstraction of the SQLAlchemy ORM.

    Creates the ORM engine & handles the creation/deletion of tables.
    Provides SessionContext-instances for use in database access.

    The class is a Singleton, so successive calls to will yield
    the same instance of this class as the first call.

    Args:
        url (str):
            The connect url to be used for connecting to the database.
            NOTE that the initial call to ORM must provide a value for
            the url; This is so that the SQLAlchemy Engine can be created.
        _purge (bool):
            If set to True, the database tables will be purged on startup.
            Defaults to False. Should not be set to True in production.
    """
    _engine: Engine
    _sessionmaker: sessionmaker

    __slots__ = "_engine", "_sessionmaker"

    def __init__(self, url: str = "", _purge: bool = False) -> None:
        if url == "":
            raise ValueError(
                "URL must be provided upon first call to ORM __init__")
        self._engine = create_engine(url=url)
        self._sessionmaker = sessionmaker(bind=self._engine)
        try:
            if _purge:
                self.purge_all()
            self.create_all()
        except OperationalError:
            logger.error(
                "Connection to database refused. Is the server running?")
            raise
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
            self, close_on_exit: bool = True) -> SessionContext:
        """Get a session context with a new session within."""
        return SessionContext(
            session=self._sessionmaker(),
            close_on_exit=close_on_exit)
