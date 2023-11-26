import json
import httpx
import pydantic

from app.core.orm import schemas
from app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=20, fh=10)

CHAINS = ("prisma", "s-market", "smarket", "alepa", "sale")


def parse_store_brand_from_string(string: str) -> str | None:
    """Parse a store brand from the start of the given string.

    Args:
        string (str): String to parse.

    Returns:
        str | None:
        Returns the titled store brand name.
        If no valid chain is found, returns None.
    """
    string = string.lower()
    if string.startswith(CHAINS):
        string = string.split()[0]
        if string == "smarket":
            return "S-market"
        return string.title()
    return None


def parse_store_response(
        response: httpx.Response
        ) -> list[schemas.StoreBase] | None:
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

    stores: list[schemas.StoreBase] = []
    for item in key:
        try:
            store = schemas.StoreBase(
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
