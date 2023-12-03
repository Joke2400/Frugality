"""Parsing functions for parsing/modifying various responses/strings."""
import re
import json
import httpx
import pydantic

from app.core.orm import schemas
from app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)

CHAINS = ("prisma", "s-market", "smarket", "alepa", "sale")


def slugify(string: str) -> str:
    """Return a 'slugified' version of the string.

    A slug is a string that can only include:
    characters, numbers, dashes, and underscores.

    Only characters "åäö" currently get replaced with
    the corresponding alphanumeric characters.

    Args:
        string (str): String to slugify.

    Returns:
        str: The slugified string.
        ex. "Name With åäö Chars" -> "name-with-aao-chars"
    """
    replaceables = {
        "å": "a",
        "ä": "a",
        "ö": "o"}
    # Split on whitespaces & remove extra whitespace between words.
    string = "-".join(string.lower().split())
    # Replace characters with corresponding alphanumeric chars.
    for char, repl in replaceables.items():
        string = re.sub(
            pattern=char,
            repl=repl,
            string=string,
            flags=re.I | re.M)
    # Remove any remaining non-alphanumeric characters.
    string = re.sub(
        pattern=r"[^a-zA-Z0-9-_]",
        repl="",
        string=string,
        flags=re.I | re.M)
    return string


def parse_store_brand_from_string(string: str) -> str | None:
    """Parse a store brand from the start of the given string.

    Args:
        string (str): String to parse.

    Returns:
        str | None:
        Returns the store brand name.
        If no valid chain is found, returns None.
    """
    string = string.lower()
    if (brand := string.split()[0]) in CHAINS:
        if brand == "smarket":
            return "s-market"
        return brand
    return None


def parse_store_response(
        response: httpx.Response
        ) -> list[schemas.Store] | None:
    """Parse stores from a httpx.Response.

    Args:
        response (httpx.Response):
            Response instance received from the API.

    Returns:
        list[schemas.StoreBase] | None:
            Returns a list of pydantic StoreBase instances.
            Returns None if an error occurred during parsing.
    """
    try:
        content = json.loads(response.text)
    except json.JSONDecodeError:
        logger.debug(
            "Could not parse response body into JSON.")
        return None
    try:
        key = content["data"]["searchStores"]["stores"]
    except KeyError:
        logger.debug(
            "Could not access stores key in response.")
        return None

    stores: list[schemas.Store] = []
    for item in key:
        try:
            store = schemas.Store(
                store_name=item.get("name"),
                store_id=item.get("id"),
                slug=item.get("slug"),
                brand=item.get("brand"))
            stores.append(store)

        except pydantic.ValidationError:
            logger.debug(
                "Store record validation failed: %s",
                item)
            continue
    stores.sort(key=lambda i: i.store_name)
    return stores
