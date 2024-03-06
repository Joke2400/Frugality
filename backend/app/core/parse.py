"""Parsing functions for parsing/modifying various responses/strings."""
import re
import json
import httpx
import pydantic

from backend.app.core.search_state import SearchState
from backend.app.core.orm import schemas
from backend.app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)

CHAINS = ("prisma", "s-market", "smarket", "alepa", "sale")


def reformat_unit_string(string: str):
    """Reformat a unit string."""
    match string:
        case "LTR":
            return "L"
        case "KGM":
            return "kg"
        case _:
            return string


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


def prepare_response_dict(response: httpx.Response) -> dict | None:
    """Convert httpx.Response to python dict.

    Returns type 'None' if a json.JSONDecodeError is raised.
    Also returns type 'None' if the given response is of that type.
    """
    try:
        content = json.loads(response.text)
    except json.JSONDecodeError as err:
        logger.debug(err)
        return None
    return content


def parse_store_response(
        response: httpx.Response,
        query: schemas.StoreQuery
        ) -> list[schemas.Store] | None:
    """Parse stores from a httpx.Response.

    Args:
        response (httpx.Response):
            Response instance received from the API.
        query (schemas.StoreQuery):
            The query that resulted in the response.
            Used for logging purposes
    Returns:
        list[schemas.Store] | None:
            Returns a list of pydantic Store instances.
            Returns 'None' if an error occurred during parsing.
    """
    logger.debug("Parsing response for query: %s.", query)
    content = prepare_response_dict(response)
    if content is None:
        logger.debug(
            "Could not parse response body into JSON for query: %s.",
            query)
        return None
    try:
        key = content["data"]["searchStores"]["stores"]
    except KeyError:
        logger.debug(
            "Could not access 'stores' key in response for query: %s.",
            query)
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
                "Store record validation failed: %s for query: '%s'",
                item, query)
            continue
    stores.sort(key=lambda i: i.store_name)
    return stores


def parse_product_to_schema(
        data: dict) -> tuple[schemas.Product, schemas.ProductData] | None:
    """Parse a product item dict into two pydantic product schemas.

    Args:
        data (dict): Dict containing a single product item.

    Returns:
        tuple[schemas.Product, schemas.ProductData] | None:
        A tuple containing Product and ProductData schemas.
        If an exception occurred during parsing, returns 'None' instead.
    """
    try:
        product = schemas.Product(
            name=data["name"],
            category=data["hierarchyPath"][0]["name"],
            ean=data["ean"],
            slug=data["slug"],
            brand=data["brandName"],
        )
        unit_prices_eur = str(float(data["price"])).split(".")
        cmp_prices_eur = str(float(data["comparisonPrice"])).split(".")

        product_data = schemas.ProductData(
            eur_unit_price_whole=int(unit_prices_eur[0]),
            eur_unit_price_decimal=int(unit_prices_eur[1]),
            eur_cmp_price_whole=int(cmp_prices_eur[0]),
            eur_cmp_price_decimal=int(cmp_prices_eur[1]),
            label_unit=reformat_unit_string(data["basicQuantityUnit"]),
            comparison_unit=reformat_unit_string(data["comparisonUnit"]),
        )
    except (KeyError, TypeError, ValueError, pydantic.ValidationError) as err:
        logger.debug("Failed to validate a product schema: %s", err)
        logger.debug("Raw data of the failed schema: %s", data)
    else:
        return product, product_data
    return None


def parse_product_response(
        response: httpx.Response,
        query: dict[str, str | int]
        ) -> tuple[
            SearchState,
            dict[str, str | int],
            list[
                tuple[
                    schemas.Product,
                    schemas.ProductData
                ]
            ]
        ]:
    """Parse product items from a response into pydantic schemas.

    Args:
        response (httpx.Response | None):
        The response object provided by the httpx library.
        If the given response is of type 'None', return an empty list of items.
        query (dict[str, str | int]):
        A dict containing the store id, query string & query category.

    Returns:
        tuple[
            SearchState
            dict[str, str | int],
            list[
                tuple[
                    schemas.Product,
                    schemas.ProductData
                ]
            ]
        ]:
        Return a tuple with the first item being a SearchState enum.
        The second item is a dict with the original query details.
        The third item is a list with all the parsed product items inside it.
        Each parsed item is a tuple containing two different pydantic schemas.
    """
    logger.debug(
        "Parsing response for query: <query='%s', store_id=%s, category='%s'>",
        query["query"], query["store_id"], query["category"])
    if (content := prepare_response_dict(response)) is None:
        return SearchState.PARSE_ERROR, query, []
    try:
        response_items = content["data"]["store"]["products"]["items"]
        store_name = content["data"]["store"]["name"]
    except (KeyError, ValueError) as err:
        logger.debug(err)
        return SearchState.PARSE_ERROR, query, []
    query["store_name"] = store_name
    if len(response_items) == 0:
        logger.debug("No items found in response body.")
        return SearchState.FAIL, query, []
    items: list[tuple[schemas.Product, schemas.ProductData]] = []
    for i in response_items:
        item = parse_product_to_schema(i)
        if not item:
            continue
        items.append(item)
    logger.debug("Parsed %s items from response.", len(items))
    return SearchState.SUCCESS, query, items
