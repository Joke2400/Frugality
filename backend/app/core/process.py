"""Contains a process singleton class for managing the application."""
from typing import Literal
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.orm import database
from app.api.routes import store_route
from app.api.routes import product_route
from app.api.routes import index as index_route
from app.utils import config, patterns
from app.utils.populate import populate_all
from app.utils.logging import LoggerManager
from app.utils.util_funcs import build_db_url

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)

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
    app: FastAPI = FastAPI()

    def __init__(self) -> None:
        logger.info("Starting FastAPI application...")
        # Add FastAPI routers
        self.app.include_router(router=index_route.router)
        self.app.include_router(router=store_route.router)
        self.app.include_router(router=product_route.router)

        # Enable CORS for frontend
        origins = ["http://localhost:5173"]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        if not config.ENV().debug:
            database.ORM(
                url=build_db_url(
                    usr=config.ENV().postgres_user,
                    passwd=config.ENV().postgres_password,
                    db=config.ENV().postgres_db,
                    testing=False))
        else:
            database.ORM(
                url=build_db_url(
                    usr=config.ENV().postgres_user,
                    passwd=config.ENV().postgres_password,
                    db=config.ENV().postgres_db,
                    testing=True),
                _purge=PURGE_DB)
            if POPULATE_DB:
                populate_all(database.ORM)
            if RUN_DEBUG_CODE:
                self._execute_debug_code()
        logger.info("FastAPI statup complete.")

    def startup(self) -> None:
        """Start the FastAPI Backend."""
        reload: bool = config.ENV().in_container
        port: Literal[80, 8080] = 80 if config.ENV().in_container else 8080
        uvicorn.run(
            app="main:fastapi.app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=reload,
            reload_includes="*.py"
        )

    @staticmethod
    def _execute_debug_code() -> None:
        """Execute debug code on startup.

        A file called 'debug.py' should be manually created to run code.
        Imports and calls execute() from the file
        NOTE: This function will not exist in final versions
        """
        logger.info("Executing debug code...")
        try:
            from debug import execute  # Breaking convention, cheers :)
            execute()
        except ImportError:
            logger.info(
                "Attempted to run debug code, but 'debug.py' was not found.")
