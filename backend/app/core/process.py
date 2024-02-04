"""Contains a process singleton class for managing the application."""
import os
from fastapi import FastAPI

from backend.app.core import config
from backend.app.core.orm import database
from backend.app.api.routes import store as store_route
from backend.app.api.routes import product as product_route
from backend.app.utils import patterns
from backend.app.utils import exceptions
from backend.app.utils.logging import LoggerManager


logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)


class Process(metaclass=patterns.SingletonMeta):
    """Singleton for managing the execution of the entire app."""
    app: FastAPI = FastAPI()
    postgres_user: str
    postgres_pass: str
    postgres_db: str

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
        postgres_port = os.getenv("POSTGRES_PORT")
        self.postgres_user = str(postgres_user)
        self.postgres_pass = str(postgres_pass)
        self.postgres_db = str(postgres_db)
        self.postgres_port = str(postgres_port)
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
        auth = f"{self.postgres_user}:{self.postgres_pass}"
        # Host must currently be manually changed
        url = f"postgresql://{auth}@PostgresDB/{self.postgres_db}"
        #url = f"postgresql://{auth}@5432:5432/db"
        return url

    @staticmethod
    def _execute_debug_code() -> None:
        """NOTE: THIS FUNCTION WILL NOT EXIST IN RELEASE VERSIONS."""
        pass
        #from debug import run
        #run()