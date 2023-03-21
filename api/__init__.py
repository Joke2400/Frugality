"""Contains API functions and strings for building graphql queries."""

from utils import LoggerManager
from .graphql_queries import queries as graphql_queries

# Cant be moved lower yet because LoggerManager needs a logic change
logger = LoggerManager.get_logger(name=__name__, stream=True)

from .skaupat_api import api_fetch_products
from .skaupat_api import api_fetch_store


__all__ = ["graphql_queries", "LoggerManager", "api_fetch_products",
           "api_fetch_store"]
