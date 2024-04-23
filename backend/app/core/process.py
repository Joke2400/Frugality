"""Contains a process singleton class for managing the application."""
import sys
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core import config
from backend.app.core.orm import database
from backend.app.api.routes import store_route
from backend.app.api.routes import product_route
from backend.app.api.routes import index as index_route
from backend.app.utils import patterns
from backend.app.utils import exceptions
from backend.app.utils.populate import populate_db
from backend.app.utils.logging import LoggerManager
from backend.app.utils.util_funcs import get_envvar

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)

load_dotenv()  # Load environment variables from .env file
RUN_DEBUG_CODE = config.parser["debug"]["run_debug_code"] in (
    "True", "true")
PURGE_DB = config.parser["debug"]["purge_db"] in (
    "True", "true")
POPULATE_DB = config.parser["debug"]["populate_db"] in (
    "True", "true")


class Process(metaclass=patterns.SingletonMeta):
    """Singleton for managing the setup of the entire app.

    Fetches environment variables & include FastAPI routers
    Configures the CORS & prepares DBContext for use.
    Also calls debug code if the debug ENVVAR is set to True.
    """
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: str | None
    container: bool = False
    app: FastAPI = FastAPI()

    def __init__(self) -> None:
        logger.info("Starting FastAPI application...")
        # Check if -'-container=True' in launch args
        for arg in sys.argv[1:]:
            if "--container" in arg:
                if arg.split("=")[1].lower() == "true":
                    self.container = True
                    break

        self.postgres_user = get_envvar("POSTGRES_USER")
        self.postgres_password = get_envvar("POSTGRES_PASSWORD")
        self.postgres_db = get_envvar("POSTGRES_DB")
        self.debug = get_envvar("DEBUG") in ("True", "true")
        try:
            # port is not necessary if running in a container
            self.postgres_port = get_envvar("POSTGRES_PORT")
        except exceptions.MissingEnvironmentVariableError as exc:
            if self.container is False:
                raise exceptions.MissingEnvironmentVariableError(
                    "Port is required when running locally.") from exc
            self.postgres_port = None

        self.app.include_router(index_route.router)
        self.app.include_router(store_route.router)
        self.app.include_router(product_route.router)

        # Enable CORS for frontend
        origins = ["http://localhost:5173"]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        if self.debug:
            logger.info("ENVIRONMENT VARIABLE 'DEBUG' IS TRUE")
            logger.info("FORCING USAGE OF TEST DATABASE")
            self.postgres_db = "test_database"
            database.ORM(
                url=self.create_database_url(), _purge=PURGE_DB)
            if POPULATE_DB:
                populate_db()
            if RUN_DEBUG_CODE:
                self._execute_debug_code()
        else:
            database.ORM(url=self.create_database_url())
        logger.info("FastAPI statup complete.")

    def create_database_url(self) -> str:
        """Create the database URL-string."""
        auth = f"{self.postgres_user}:{self.postgres_password}"
        host = f"localhost:{self.postgres_port}/{self.postgres_db}"
        if self.container:
            host = f"postgres_db/{self.postgres_db}"

        logger.info(f"Set postgres host to @{host}")
        return f"postgresql://{auth}@{host}"


    @staticmethod
    def _execute_debug_code() -> None:
        """Execute debug code on startup.

        A file called 'debug.py' should be manually created to run code.
        Imports and calls execute() from the file
        NOTE: This function will not exist in final versions
        """
        logger.info("Executing debug code...")
        try:
            from backend.debug import execute  # Breaking convention, cheers :)
            execute()
        except ImportError:
            logger.info(
                "Attempted to run debug code, but 'debug.py' was not found.")
