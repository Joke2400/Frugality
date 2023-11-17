"""Contains a process singleton class for managing the application."""
import os
from fastapi import FastAPI

from app.utils.patterns import SingletonMeta
from app.utils.exceptions import MissingEnvironmentVar
from app.core.orm import DBContext
from app.api.routes.store import router


class Process(metaclass=SingletonMeta):
    """Singleton for managing the execution of the entire app."""

    app: FastAPI = FastAPI()

    def __init__(self) -> None:
        """Initialize app routes & fetch environment variables."""
        if (postgres_user := os.getenv("POSTGRES_USER")) in (None, ""):
            raise MissingEnvironmentVar(
                "ENVIRONMENT VAR 'POSTGRES_USER' WAS NOT SUPPLIED")
        if (postgres_pass := os.getenv("POSTGRES_PASSWORD")) in (None, ""):
            raise MissingEnvironmentVar(
                "ENVIRONMENT VAR 'POSTGRES_PASSWORD' WAS NOT SUPPLIED")
        if (postgres_db := os.getenv("POSTGRES_DB")) in (None, ""):
            raise MissingEnvironmentVar(
                "ENVIRONMENT VAR 'POSTGRES_DB' WAS NOT SUPPLIED")    

        self.db_user: str = str(postgres_user)
        self.db_pass: str = str(postgres_pass)
        self.db: str = str(postgres_db)
        self.app.include_router(router)

        # This check will be removed in final versions.
        if bool(os.getenv("DEBUG")):
            DBContext.prepare_context(
                url=self.get_database_url(),
                purge_all_tables=True)  # Reset database tables in debug mode
            self._execute_debug_code()
        else:
            DBContext.prepare_context(
                url=self.get_database_url())

    def get_database_url(self) -> str:
        """Get database URL string."""
        auth = f"{self.db_user}:{self.db_pass}"
        # Host must currently be manually changed
        url = f"postgresql://{auth}@localhost:5432/{self.db}"
        return url

    @staticmethod
    def _execute_debug_code() -> None:
        """NOTE: THIS FUNCTION WILL NOT EXIST IN RELEASE VERSIONS."""
        if os.getenv("DEBUG"):
            from debug import run
            run()
