"""TEMP"""
from enum import Enum
from configparser import ConfigParser
from ariadne import load_schema_from_path
from app.utils import ProjectPaths

config = ConfigParser()
config.read(ProjectPaths.settings_path())

USER_AGENT = config["API"]["user_agent"]
GRAPHQL_ENDPOINT = config["SKAUPAT_URLS"]["api_graphql"]

# Load graphql schema from static files
PRODUCT_GRAPHQL = load_schema_from_path(
    path=ProjectPaths.graphql_path() / "product.graphql")
STORE_GRAPHQL = load_schema_from_path(
    path=ProjectPaths.graphql_path() / "store.graphql")


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
        operation: Operation, variables: dict, timeout: int = 10):
    """Build the request parameters dictionary."""
    return {
        "timeout": timeout,
        "headers": build_headers_dict(),
        "json": build_json_dict(operation, variables)
    }