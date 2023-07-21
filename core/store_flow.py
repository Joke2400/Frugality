"""Contains functions for initiating, managing and parsing a store search."""

import re
from typing import Any, Callable
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from api import fetch_store_from_api

from utils import Pending
from utils import Success
from utils import Fail
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
    """Convert string to alphanumeric.

    Result includes a-z as well as åäö.

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
            logger.debug("Received an empty string to parse.")

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
            search.state = Fail()
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
            search.set_result(response, ParseFailed())

    if len(stores) == 0:
        search.state = Fail()
    else:
        stores.sort(key=lambda i: i.name)
        search.set_result(stores, Success())
    return search


def string_parse_wrapper(search_func: Callable) -> Callable:
    """Wrap a store search function with parsing functionality."""
    def wrapper(search: Search) -> Search:
        if isinstance(search.query, str):
            parsed_data = parse_store_from_string(string=search.query)
            if not any(parsed_data):
                search.state = ParseFailed()
                return search
            search.set_query(Store(*parsed_data), Pending())
        return search_func(search=search)
    return wrapper


@string_parse_wrapper
def db_store_search(search: Search) -> Search:
    """Search for stores in the local database.

    The passed in Search object gets modified depending on results with
    it's state indicating what has happened during execution.

    Possible return states:
        <Success>: Stores were successfully found in database.
        <Fail>: Stores could not be found in the database.

    NOTICE: db_search() currently only returns a single result
    if the id/string matches exactly. In the future, the function
    filter_query() will be reworked with a better search algorithm.
    """
    store = search.query
    logger.debug("Fetching %s from DB...", store)

    if store.store_id:  # If id exists query using that.
        query = {"store_id": store.store_id}
    else:  # Otherwise query by using slug.
        query = {"slug": str(store.slug)}

    try:
        resp = core.manager.filter_query(StoreModel, query).one()
    except (NoResultFound, MultipleResultsFound):
        logger.debug("Could not fetch %s from DB.", store)
        search.set_result(None, Fail())
    else:
        store.set_fields(resp.name, resp.store_id, resp.slug)
        search.set_result([store], Success())
    return search


@string_parse_wrapper
def api_store_search(search: Search) -> Search:
    """Search for stores from the API.

    The passed in Search object gets modified depending on results with
    it's state indicating what has happened during execution.

    Possible return states:
        <Success>: Stores were successfully parsed from the response.
        <Fail>: Stores could not be found in the response.
        <ParseFailed>: The response could not be parsed.
        <NoResponse>: The API did not return a response.
    """
    logger.debug("Fetching %s from API...", search.query.name)
    response = fetch_store_from_api(
        store_query=(search.query.name, search.query.store_id))
    if response:
        search = parse_response(search=search, response=response)
    else:
        search.state = NoResponse()
    return search


def execute_db_search(search: Search) -> Search:
    """Query the DB by calling the search function and log the result."""
    logger.debug("[Store search]: Querying database.")
    search = db_store_search(search=search)
    logger.debug("Database search: ('%s')", search.state)
    match search.state:

        case Success():
            logger.debug(
                "Database query for '%s', was successful!",
                search.query)

        case Fail():
            logger.debug(
                "Could not find results for query '%s' from database.",
                search.query)

        case ParseFailed():
            logger.debug(
                "Parsing of query string failed for query: '%s'",
                search.query)
            search.feedback = "Error parsing query string."

        case _:
            logger.debug(
                "search.state reached an invalid state during execution. %s",
                search)
            # At this point we want the match statement in app.store_query()
            # to fall back on the ('case _: or 'other') case.
            search.state = Pending()

    return search


def execute_api_search(search: Search) -> Search:
    """Query the API by calling the search function and log the result."""
    logger.debug("[Store search]: Querying api.")
    search = api_store_search(search=search)
    logger.debug("API search: ('%s')", search.state)
    match search.state:

        case Success():
            logger.debug(
                "API query for '%s', was successful!",
                search.query)
            # THIS NEXT PART WILL IN THE FUTURE BE CALLED AFTER THE
            # RESPONSE HAS BEEN SENT TO THE CLIENT.
            # USING Flask after_request()
            # -----------------------------------------
            count = 0
            for store in search.result:
                result = core.manager.add_store(
                    store=store)
                if result:
                    count += 1
            logger.debug("Added %s out of %s stores to db.",
                         count, len(search.result))
            # -----------------------------------------

        case Fail():
            logger.debug(
                "Could not find results for query '%s' from API.",
                search.query)

        case ParseFailed():
            logger.debug(
                "Failed to parse response %s for query '%s'",
                search.result, search.query)
            search.feedback = "Error parsing API response."

        case NoResponse():
            logger.debug(
                "Response from API was invalid or empty.")

        case _:
            logger.debug(
                "search.state reached an invalid state during execution. %s",
                search)
            # At this point we want the match statement in app.store_query()
            # to fall back on the ('case _: or 'other') case.
            search.state = Pending()

    return search


def execute_store_search(value: Any) -> Search:
    """Execute a store search using the query provided.

    Simply calls the api search if the db search yielded no results.

    Returns a Search object with a state field indicating the result
    of the search. The state gives context on what to do with the data
    returned, and each possible state should be handled by the function
    that calls this one.
    """
    logger.debug("[Store search]: Begun a new store search!")
    search = execute_db_search(search=Search(query=value, state=Pending()))
    if search.state is Fail():
        return execute_api_search(search=search)
    return search


def add_store_query(request: dict, stores: list[tuple[str, str, str]]
                    ) -> tuple[list[tuple[str, str, str]], int]:
    """Append a store query to the provided stores list.

    Returns the same list that was passed in with potential
    changes applied. The integer returned indicates the status code
    that the server should return with.
    """
    logger.debug("Attempting to add a store to the stores list...")
    key: Any = request.get("store", None)
    if not isinstance(key, list):
        return stores, 400
    key = tuple(map(str, key))
    store: tuple[str, str, str] = key[:3]
    if not all(store):
        return stores, 400
    if store not in stores:
        if not len(stores) >= 5:
            stores.append(store)
            logger.debug("Added store %s, to store queries.", store)
            return stores, 201
    return stores, 404


def remove_store_query(request: dict, stores: list[tuple[str, str, str]]
                       ) -> tuple[list[tuple[str, str, str]], int]:
    """Remove a store from the provided stores list.

    Returns the same list that was passed in with potential
    changes applied. The integer returned indicates the status code
    that the server should return with.
    """
    logger.debug("Attempting removal of a store from the stores list.")
    store_id: Any = request.get("id", None)
    if not isinstance(store_id, str):
        return stores, 400
    results = list(filter(lambda i: i[1] == store_id, stores))
    if len(results) > 0:
        stores.remove(results[0])
        logger.debug("Removed store %s, from store queries.", results[0])
        return stores, 200
    return stores, 404
