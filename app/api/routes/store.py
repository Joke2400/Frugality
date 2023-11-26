from fastapi import APIRouter, HTTPException

from app.utils import LoggerManager
from app.core import search
from app.core.orm import schemas, models
from app.core import parse


logger = LoggerManager().get_logger(__name__, sh=20, fh=10)
router = APIRouter()


@router.get("/stores/{store_name}", response_model=list[schemas.StoreBase])
async def get_store_by_name(
        store_name: str
        ) -> list[models.Store] | list[schemas.StoreBase]:
    """Route that returns a single store record by searching by its name."""
    logger.debug("Retrieving store by name: %s", store_name)
    store_name = store_name.strip()
    query = schemas.StoreQuery(
        **{"store_name": store_name,
           "brand": parse.parse_store_brand_from_string(store_name)})

    # Search from DB
    context = search.SearchContext(
        strategy=search.DBStoreNameSearchStrategy())
    data = await context.execute(query=query)
    if data[0] is search.State.SUCCESS:
        return data[1]
    logger.debug(
        "Database search yielded no matching results for %s",
        store_name)

    # Search from API
    context = search.SearchContext(  # TODO: fix linting error here
        strategy=search.APIStoreNameSearchStrategy())
    match await context.execute(query=query):
        case [search.State.SUCCESS, list(), str()] as data:
            return data[1]
        case [search.State.FAIL | search.State.NO_RESPONSE,
              list(), str()] as data:
            raise HTTPException(status_code=404, detail=data[2])
        case [search.State.PARSE_ERROR, list(), str()] as data:
            raise HTTPException(status_code=500, detail=data[2])
        case _ as data:
            raise ValueError(
                f"Search returned an unexpected value: {data}")
