"""Contains a process singleton class for managing the application."""
import os
from pathlib import Path
from fastapi import FastAPI

from app.api.routes.store import router
from app.utils.patterns import SingletonMeta
from app.utils.exceptions import MissingEnvironmentVar

from app.utils import LoggerManager


class Process(metaclass=SingletonMeta):
    """Singleton for managing the execution of the entire app."""

    app: FastAPI = FastAPI()
    logger_manager = LoggerManager(
        log_path=Path.cwd() / "app" / "data" / "logs",
        purge_old_logs=True
    )

    def __init__(self) -> None:
        """Initialize app routes & fetch environment variables."""
        if (db_user := os.getenv("POSTGRES_USER")) in (None, ""):
            raise MissingEnvironmentVar(
                "ENVIRONMENT VAR 'POSTGRES_USER' WAS NOT SUPPLIED")
        if (db_password := os.getenv("POSTGRES_PASSWORD")) in (None, ""):
            raise MissingEnvironmentVar(
                "ENVIRONMENT VAR 'POSTGRES_PASSWORD' WAS NOT SUPPLIED")
        self.db_user: str = str(db_user)
        self.db_password: str = str(db_password)
        self.app.include_router(router)
        self._execute_debug_code()

    @staticmethod
    def _execute_debug_code():
        """NOTE: THIS FUNCTION WILL NOT EXIST IN RELEASE VERSIONS."""
        if os.getenv("DEBUG"):
            from debug import run
            run()
