"""Contains functions for initiating, managing and parsing a store search."""

import re
from typing import Any, Callable
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from api import api_fetch_store

from utils import Pending
from utils import Success
from utils import NoResults
from utils import ParseFailed
from utils import NoResponse
from utils import regex_findall
from utils import LoggerManager

import core
from .store import Store
from .search import Search
from .orm import Store as StoreModel

logger = LoggerManager.get_logger(name=__name__)


def convert_to_alphanumeric(string: str) -> str:
    """Convert string to alphanumeric(+åäö).

    If input string is not of correct type or
    not parseable, return an empty string instead.
    """
    try:
        s_query = re.sub(
            pattern=r"[^a-zA-Z0-9\såäö-]",
            repl="",
            string=str(string.strip()),
            flags=re.I | re.M)
        return s_query
    except TypeError as err:
        logger.exception(
            "Could not convert %s to alphanumeric: %s",
            string, err)
        return ""


def parse_store_from_string(
        string: str) -> tuple[str | None, str | None, str | None]:
    """Parse store name, id and slug from string, if present.

    Args:
        string (str): String to parse.

    Returns:
        tuple[str | None]: Returns name, id and slug as optional values.
    """
    string = convert_to_alphanumeric(string)
    logger.debug("Parsing store from string: '%s'", string)
    data = regex_findall(
        r"\d+|^(?:\s*\b)\b[A-Za-zåäö\s-]+(?=\s?)", string)

    def is_digits(string: Any) -> str | None:
        try:
            i = str(int(string.strip()))
        except ValueError:
            return None
        return i

    s_name, s_id, slug = None, None, None
    match data:

        case [str(), str()] as data:
            try:
                s_name = str(data[0]).strip()
                slug = "-".join(s_name.lower().split())
            except ValueError as err:
                logger.exception(err)
            if i := is_digits(data[1]):
                s_id = i

        case [str()] as data:
            if i := is_digits(data[0]):
                s_id = i
            else:
                try:
                    s_name = str(data[0]).strip()
                    slug = "-".join(s_name.lower().split())
                except ValueError as err:
                    logger.exception(err)
        case _:
            logger.debug("String was empty.")

    logger.debug("Data parsed from string: ('%s', '%s', '%s')",
                 s_name, s_id, slug)
    return (s_name, s_id, slug)


def parse_response(search: Search, response: dict) -> Search:
    """Parse stores from response dict.

    Returned value is the same Search instance passed in.
    Parsed stores are placed in the result field of the instance.
    """
    logger.debug("Parsing response from API...")
    key = None
    try:
        key = response["data"]["searchStores"]["stores"]
        logger.debug("Total store count: %s.",
                     response["data"]["searchStores"]["totalCount"])
    except KeyError:
        logger.debug("Response did not contain multiple stores.")
        try:
            key = response["data"]["store"]
        except KeyError:
            logger.debug("Response contained no stores.")
            search.state = NoResults()
            return search

    stores = []
    match key:

        case list():
            for i in key:
                name, s_id = i.get("name"), i.get("id")
                if name is None or s_id is None:
                    continue
                slug = "-".join(name.lower().split())
                stores.append(Store(name, s_id, slug))

        case dict():
            name, s_id = key.get("name"), key.get("id")
            if name is not None or s_id is not None:
                slug = "-".join(name.lower().split())
                stores.append(Store(name, s_id, slug))

        case _:
            search.state = ParseFailed()

    if len(stores) == 0:
        search.state = NoResults()
    else:
        stores.sort(key=lambda i: i.name)
        search.set_result(stores, Success())
    return search


def store_api_search(search: Search) -> Search:
    """Query api for a store and return the response."""
    logger.debug("Fetching %s from API...", search.query.name)
    response = api_fetch_store(
        query_data=(search.query.name, search.query.store_id))
    if response:
        search.set_result(response, Success())
    else:
        search.state = NoResponse()
    return search


def store_db_search(search: Search) -> Search:
    """Get store from database and return the result."""
    logger.debug("Fetching %s from DB...", search.query)
    store = search.query
    if store.store_id:  # If ID exists do this
        query = {"store_id": store.store_id}
    else:  # Otherwise query by using slug
        query = {"slug": str(store.slug)}
    try:
        resp = core.manager.filter_query(StoreModel, query).one()
    except (NoResultFound, MultipleResultsFound):
        logger.debug("Could not fetch %s from DB.", store)
    else:
        store.set_fields(resp.name, resp.store_id, resp.slug)
        search.set_result([store], Success())
    return search


def store_search(search: Search, func: Callable) -> Any:
    """Call the search func with the given store as a parameter."""
    if isinstance(search.query, str):
        parsed_data = parse_store_from_string(string=search.query)
        if not any(parsed_data):
            search.state = ParseFailed()
            return search
        search.set_query(Store(*parsed_data), Pending())
    return func(search=search)


def execute_store_search(value: Any) -> Search:
    """Execute a store search."""
    search = Search(query=str(value), state=Pending())
    logger.info("[Initiated a new store search]")
    search = store_search(search=search, func=store_db_search)
    logger.debug("Search (%s)", search.state)
    match search.state:

        case Success():
            logger.debug(
                "Database search for query %s, was successful!",
                search.query)
            return search

        case ParseFailed():
            logger.debug(
                "Parsing of store failed for query: %s",
                search.query)
            search.result = "Error parsing string."
            return search
    # If program reaches here, search.state = Pending()
    search = store_search(search=search, func=store_api_search)
    if search.state == NoResponse():
        logger.debug("Received no response from API.")
        return search
    search = parse_response(search=search, response=search.result)
    logger.debug("Search (%s)", search.state)
    match search.state:

        case Success():
            logger.debug(
                "Success! Parsed %s stores, from query %s.",
                len(search.result), search.query)
            # THIS WILL BE MOVED TO FLASK AFTER_REQUEST
            count = 0
            for store in search.result:
                result = core.manager.add_store(
                    store=store)
                if result:
                    count += 1
            logger.debug("Added %s out of %s stores to db.",
                         count, len(search.result))
            return search

        case ParseFailed():
            logger.debug(
                "Failed to parse response:  %s",
                search.result)
            search.result = "Error parsing response."

        case _:
            logger.debug(
                "Parsed no stores from response.")
    return search


def add_store_query(request_json: dict, stores: list[tuple[str, str, str]]
                    ) -> list[tuple[str, str, str]]:
    """Append a store query to the provided stores list."""
    key: Any = request_json.get("store", None)
    if not isinstance(key, list):
        return stores
    key = tuple(map(str, key))
    store: tuple[str, str, str] = key[:3]
    if not all(store):
        return stores
    if store not in stores:
        if not len(stores) >= 5:
            stores.append(store)
            logger.debug("Added store %s, to store queries.", store)
    return stores


def remove_store_query(request_args: dict, stores: list[tuple[str, str, str]]
                       ) -> list[tuple[str, str, str]]:
    """Remove a store from the provided stores list."""
    store_id: Any = request_args.get("id", None)
    if not isinstance(store_id, str):
        return stores
    results = list(filter(lambda i: i[1] == store_id, stores))
    if len(results) > 0:
        stores.remove(results[0])
        logger.debug("Removed store %s, from store queries.", results[0])
    return stores
