"""Functions for creating request payloads."""
from typing import Any, TypeAlias, TypeVar
from enum import Enum
from ariadne import load_schema_from_path

from app.utils import config, paths

USER_AGENT = str(config.parser["api"]["user_agent"])
GRAPHQL_ENDPOINT = config.parser["skaupat_urls"]["api_graphql"]

# Load graphql schema from static files
PRODUCT_GRAPHQL = load_schema_from_path(
    path=paths.Project.graphql_path() / "product.graphql")
STORE_GRAPHQL = load_schema_from_path(
    path=paths.Project.graphql_path() / "store.graphql")

BasicJsonType: TypeAlias = str | int | float | bool | None
JsonType: TypeAlias = \
    BasicJsonType | list[BasicJsonType] | dict[str, BasicJsonType]
JsonTypeT_co = TypeVar("JsonTypeT_co", covariant=True, bound=JsonType)
# Gotta love the dynamic typing life


class Operation(str, Enum):
    """String enum for graphql operation types."""
    PRODUCT_SEARCH = "GetProductByName"
    STORE_SEARCH = "StoreSearch"


def build_request_headers() -> dict[str, str]:
    """Build & return the request headers dict."""
    return {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "User-Agent": USER_AGENT,
        # Required for the api to respond:
        "x-client-name": "skaupat-web"
    }


def build_graphql_request_body(
        operation: Operation,
        variables: dict[str, JsonTypeT_co]
        ) -> dict[str, str | dict[str, JsonTypeT_co]]:
    """Build & return a GraphQL request body dict.

    Contains operation_name, query and variables.
    See the GraphQL docs online for details about the format.
    """
    match operation:
        case operation.PRODUCT_SEARCH:
            query = PRODUCT_GRAPHQL
        case operation.STORE_SEARCH:
            query = STORE_GRAPHQL
    return {
        "operation_name": operation.value,
        "query": query,
        "variables": variables
    }


def build_request_payload(
        method: str, operation: Operation,
        variables: dict[str, JsonTypeT_co],
        timeout: int = 10) -> dict[str, Any]:
    """Build & return the request parameters dict."""
    return {
        "method": method,
        "url": GRAPHQL_ENDPOINT,
        "timeout": timeout,
        "headers": build_request_headers(),
        "json": build_graphql_request_body(operation, variables)
    }


def build_store_variables(value: str) -> dict[str, str | None]:
    """Build the required GraphQL variables dict.

    This function returns the appropriate variables for
    the STORE_SEARCH operation.
    """
    return {
        "StoreBrand": None,
        "cursor": None,
        "query": value}


def build_product_variables(
        store_id: int,
        query: str,
        category: str,
        limit: int = 24) -> dict[str, int | str]:
    """Build the required GraphQL variables dict.

    This function returns the appropriate variables for
    the PRODUCT_SEARCH operation.
    """
    return {
        "StoreID": store_id,
        "query": query,
        "slugs": category,
        "limit": limit
    }
