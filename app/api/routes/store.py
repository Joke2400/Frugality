from fastapi import APIRouter, HTTPException

from app.utils import LoggerManager
from app.core import search
from app.core.orm import schemas


logger = LoggerManager().get_logger(__name__, sh=20, fh=10)
router = APIRouter()


@router.get("/stores/{store_name}", response_model=list[schemas.StoreIn])
async def get_store_by_name(store_name: str):
    """Route that returns a single store record by searching by its name."""
    logger.debug("Retrieving store by name: %s", store_name)
    query = schemas.StoreQuery(**{"store_name": store_name, "store_id": None})
    context = search.SearchContext(
        strategy=search.DBStoreNameSearchStrategy())
    match await context.execute(query=query):
        case _:
            pass

    context.strategy = search.APIStoreNameSearchStrategy()
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
