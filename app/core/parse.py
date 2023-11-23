import json
import httpx
import pydantic

from app.core.orm import schemas
from app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=20, fh=10)


def parse_store_response(
        response: httpx.Response) -> list[schemas.StoreIn] | None:
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

    stores: list[schemas.StoreIn] = []
    for item in key:
        try:
            store = schemas.StoreIn(
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
