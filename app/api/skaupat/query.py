"""TEMP"""
from enum import Enum
from typing import Any
from ariadne import load_schema_from_path

from app.api import request
from app.core import config, parse
from app.core.orm import schemas
from app.utils import paths

USER_AGENT = str(config.parser["API"]["user_agent"])
GRAPHQL_ENDPOINT = config.parser["SKAUPAT_URLS"]["api_graphql"]

# Load graphql schema from static files
PRODUCT_GRAPHQL = load_schema_from_path(
    path=paths.Project.graphql_path() / "product.graphql")
STORE_GRAPHQL = load_schema_from_path(
    path=paths.Project.graphql_path() / "store.graphql")


class Operation(str, Enum):
    """Enumeration for graphql operation types."""
    PRODUCT_SEARCH = "GetProductByName"
    STORE_SEARCH = "StoreSearch"


def build_headers_dict() -> dict:
    """Build the request 'headers' field dict."""
    return {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "User-Agent": USER_AGENT,
        # Required for the api to respond:
        "x-client-name": "skaupat-web"
    }


def build_json_dict(operation: Operation, variables: dict):
    """Build the request 'json' field dict."""
    if not isinstance(operation, Operation):
        raise TypeError(
            "Operation must be of Enum type 'Operation'")
    match operation:
        case operation.PRODUCT_SEARCH:
            query = PRODUCT_GRAPHQL
        case operation.STORE_SEARCH:
            query = STORE_GRAPHQL
        case _:
            raise ValueError(
                "Provided operation type was undefined.")
    return {
        "operation_name": operation.value,
        "query": query,
        "variables": variables
    }


def build_request_params(
        method: str, operation: Operation,
        variables: dict, timeout: int = 10):
    """Build the request parameters dictionary."""
    return {
        "method": method,
        "url": GRAPHQL_ENDPOINT,
        "timeout": timeout,
        "headers": build_headers_dict(),
        "json": build_json_dict(operation, variables)
    }


def build_store_search_vars(value: str) -> dict:
    """Build the variables dict for use in a store search."""
    return {
        "StoreBrand": None,
        "cursor": None,
        "query": value}


def build_product_search_vars(
        query: dict[str, str | int],
        limit: int = 24) -> dict:
    """Build the variables dict for use in a product search."""
    return {
        "StoreID": query["store_id"],
        "query": query["query"],
        "slugs": query["slugs"],
        "limit": limit
    }


async def send_product_query(
        query: dict[str, str | int], params: dict[str, Any]
        ) -> tuple[
            dict[str, str | int],
            list[
                tuple[
                    schemas.Product,
                    schemas.ProductData
                ]
            ]
        ]:
    """Send a product query to the external API and then parse it.

    This function is essentially a wrapper for the request.send_request() func.
    The intent is to allow the call to asyncio.gather() to parse the retrieved
    responses immediately, while still waiting for the others to finish.

    TODO: Consider a better location to place this function.


    Args:
        query (dict[str, str  |  int]):
        A dict containing the store id, query string & query category.
        params (dict[str, Any]):
        The request & query parameters to be used with the request.

    Returns:
        tuple[
            dict[str, str | int],
            list[
                tuple[
                    schemas.Product,
                    schemas.ProductData
                ]
            ]
        ]:
        Returns tuple with the first item being a dict with the query details.
        The second item is a list with all the parsed product items inside it.
        Each parsed item is a tuple containing two different pydantic schemas.
    """
    response = await request.send_request(params=params)
    return parse.parse_product_response(
        response=response,
        query=query
    )
