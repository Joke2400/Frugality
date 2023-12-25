"""Contains a process singleton class for managing the application."""
import os
from fastapi import FastAPI

from app.utils import patterns
from app.utils import exceptions
from app.core.orm import database
from app.api.routes import store as store_route
from app.api.routes import product as product_route
from app.core import config


class Process(metaclass=patterns.SingletonMeta):
    """Singleton for managing the execution of the entire app."""
    app: FastAPI = FastAPI()
    db_user: str
    db_pass: str
    db: str

    def __init__(self, in_container: bool = False) -> None:
        """Initialize app routes & fetch environment variables."""
        if (postgres_user := os.getenv("POSTGRES_USER")) in (None, ""):
            raise exceptions.MissingEnvironmentVar(
                "ENVIRONMENT VAR 'POSTGRES_USER' WAS NOT SUPPLIED")
        if (postgres_pass := os.getenv("POSTGRES_PASSWORD")) in (None, ""):
            raise exceptions.MissingEnvironmentVar(
                "ENVIRONMENT VAR 'POSTGRES_PASSWORD' WAS NOT SUPPLIED")
        if (postgres_db := os.getenv("POSTGRES_DB")) in (None, ""):
            raise exceptions.MissingEnvironmentVar(
                "ENVIRONMENT VAR 'POSTGRES_DB' WAS NOT SUPPLIED")
        self.db_user = str(postgres_user)
        self.db_pass = str(postgres_pass)
        self.db = str(postgres_db)
        self.app.include_router(store_route.router)
        self.app.include_router(product_route.router)

        # This check will be removed in final versions.
        if bool(config.parser["APP"]["debug"]):
            database.DBContext.prepare_context(
                url=self.get_database_url(in_container),
                purge_all_tables=True)  # Reset database tables in debug mode
            self._execute_debug_code()
        else:
            database.DBContext.prepare_context(
                url=self.get_database_url(in_container))

    def get_database_url(self, in_container: bool = False) -> str:
        """Get database URL string."""
        auth = f"{self.db_user}:{self.db_pass}"
        # Host must currently be manually changed
        url = f"postgresql://{auth}@localhost:5432/{self.db}"
        #url = f"postgresql://{auth}@5432:5432/db"
        return url

    @staticmethod
    def _execute_debug_code() -> None:
        """NOTE: THIS FUNCTION WILL NOT EXIST IN RELEASE VERSIONS."""
        from debug import run
        run()
