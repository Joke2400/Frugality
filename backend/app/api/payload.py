"""Functions for creating request payloads."""
from enum import Enum
from ariadne import load_schema_from_path

from backend.app.core import config
from backend.app.utils import paths

USER_AGENT = str(config.parser["api"]["user_agent"])
GRAPHQL_ENDPOINT = config.parser["skaupat_urls"]["api_graphql"]

# Load graphql schema from static files
PRODUCT_GRAPHQL = load_schema_from_path(
    path=paths.Project.graphql_path() / "product.graphql")
STORE_GRAPHQL = load_schema_from_path(
    path=paths.Project.graphql_path() / "store.graphql")


class Operation(str, Enum):
    """Enumeration for graphql operation types."""
    PRODUCT_SEARCH = "GetProductByName"
    STORE_SEARCH = "StoreSearch"


def build_request_headers() -> dict:
    """Build the request headers."""
    return {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "User-Agent": USER_AGENT,
        # Required for the api to respond:
        "x-client-name": "skaupat-web"
    }


def build_graphql_request_body(operation: Operation, variables: dict):
    """Build a GraphQL request body.

    Contains operation_name, query and variables.
    See GraphQL docs online for details.
    """
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


def build_request_payload(
        method: str, operation: Operation,
        variables: dict, timeout: int = 10):
    """Build the request parameters dictionary."""
    return {
        "method": method,
        "url": GRAPHQL_ENDPOINT,
        "timeout": timeout,
        "headers": build_request_headers(),
        "json": build_graphql_request_body(operation, variables)
    }


def build_store_variables(value: str) -> dict:
    """Build the required GraphQL variables dict.

    In this case the variables required when the operation name is:
        operation.STORE_SEARCH.
    """
    return {
        "StoreBrand": None,
        "cursor": None,
        "query": value}


def build_product_variables(
        store_id: int,
        query: dict[str, str],
        limit: int = 24) -> dict:
    """Build the required GraphQL variables dict.

    In this case the variables required when the operation name is:
        operation.PRODUCT_SEARCH.
    """
    return {
        "StoreID": store_id,
        "query": query["query"],
        "slugs": query["category"],
        "limit": limit
    }
