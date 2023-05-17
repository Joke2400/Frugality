"""Contains functions for initiating, managing and parsing a store search."""

import re
from typing import Any
from sqlalchemy.exc import NoResultFound

from api import api_fetch_store

from utils import Found
from utils import NotFound
from utils import QueryPending
from utils import ParseFailed
from utils import regex_findall
from utils import LoggerManager

import core
from .store import Store
from .orm import Store as db_Store

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


def parse_store_from_response(store: Store, response: dict) -> Store:
    """Parse store from response and return result as a Store object.

    Args:
        store (Store): Store query object.
        response (dict): Response dict received through api.

    Returns:
        Store: Return Store with new data or with updated state.
    """
    logger.debug("Parsing response from API...")
    key = None
    try:  # Find correct keys in response dict.
        key = response["data"]["searchStores"]["stores"]
    except KeyError:
        logger.debug("Response did not contain multiple stores.")
        try:
            key = response["data"]["store"]
        except KeyError:
            logger.debug("Response contained no stores.")
            store.state = NotFound()

    match key:

        case list():
            for i in key:
                if "-".join(i["name"].lower().split()) == store.slug:
                    return Store(i.get("name"), i.get("id"),
                                 store.slug, Found())
            logger.debug("Could not find store in response items.")
            store.state = NotFound()

        case dict():
            if key["id"].strip() == store.store_id:
                slug = "-".join(str(key.get("name")).lower().split())
                return Store(key.get("name"), key.get("id"),
                             slug, Found())
            logger.debug("Could not match found store slug.")
            store.state = NotFound()

        case _:
            store.state = ParseFailed()

    return store


def get_store_from_api(store: Store) -> Store:
    """Get store from api and parse the results.

    Args:
        store (Store): Store to query.

    Returns:
        Store: Store state is either Found() or NotFound().
    """
    logger.debug("Fetching %s from API...", store)
    response = api_fetch_store(query_data=(store.name, store.store_id))
    if not response:
        logger.debug("Received no response from API.")
        store.state = NotFound()
        return store
    return parse_store_from_response(store=store, response=response)


def get_store_from_db(store: Store) -> Store:
    """Get store from database and return the result.

    Passed in store object gets modified if store is found.

    Args:
        store (Store): Store to query.

    Returns:
        Store: State is set to Found() if store is in database.
            If it's not found, state will remain unmodified.
    """
    logger.debug("Fetching %s from DB...", store)
    if store.store_id:  # If ID exists do this
        db_query = {"store_id": store.store_id}
    else:  # Otherwise query by using slug
        db_query = {"slug": str(store.slug)}
    try:
        results = core.manager.filter_query(db_Store, db_query).one()
    except NoResultFound:
        logger.debug("Could not find %s in DB.", store)
    else:
        store.set_fields(results[0].name, results[0].id,
                         results[0].slug)
        store.state = Found()
    return store


def execute_store_search(string: str) -> Store:
    """Search for store in database and api.

    Takes in a string.
    Given string gets parsed, queried and then validated
    before being added to stores list if not already present.
    If store does not exist in database, adds it.

    Returns a Store() instance with a state field indicating
    what to do with the returned store data.
    """
    logger.info("[Initiated a new store search]\n")
    parsed_data = parse_store_from_string(string=string)
    if not any(parsed_data):
        return Store(state=ParseFailed())

    store = Store(*parsed_data, QueryPending())
    store = get_store_from_db(store=store)
    if store.state is Found():
        return store

    store = get_store_from_api(store=store)
    if store.state is Found():
        result = core.manager.add_store(store=store)
        if not result:
            logger.debug(
                "Unable to add store: (%s, %s, %s)",
                result[1].store_id, result[1].name, result[1].slug)
    return store


def remove_store_query(stores: list[tuple], request_json: dict) -> list[tuple]:
    """Remove a store from the provided stores list."""
    if len(stores) > 0:
        try:
            index = int(request_json["index"])
            item = stores[index]
        except (KeyError, ValueError, IndexError) as err:
            logger.exception(err)
        else:
            stores.remove(item)
    return stores
