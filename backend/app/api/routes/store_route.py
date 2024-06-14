"""API routes for store retrieval."""
from typing import cast
from fastapi import (
    APIRouter,
    BackgroundTasks
)
from app.core.orm import schemas
from app.core.search.store_flow import (
    DBStoreSearchStrategy,
    APIStoreSearchStrategy
)
from app.core.search.context import SearchContext
from app.utils.logging import LoggerManager
from app.utils.util_funcs import assert_never

router = APIRouter()
logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
resultT = list[schemas.Store | schemas.StoreDB[schemas.ProductDataDB]]


@router.post("/stores/", response_model=schemas.StoreResponse)
async def get_stores(
            query: schemas.StoreQuery,
            background_tasks: BackgroundTasks
        ) -> schemas.StoreResponse:
    """TODO: Redo docstring"""
    logger.info("Performing new StoreSearch...")
    # Search the database
    with SearchContext(
            background_tasks=background_tasks,
            strategy=DBStoreSearchStrategy()) as context:
        results: resultT = cast(
            resultT, await context.execute(user_query=query))
        if len(results) != 0:
            # Schema handles the conversion of StoreDB to Store
            response = schemas.StoreResponse(results=results)
            logger.info("Returning: %s", response)
            return response

    # If no results from database, search the API
    with SearchContext(
            background_tasks=background_tasks,
            strategy=APIStoreSearchStrategy()) as context:
        results = cast(
            resultT, await context.execute(user_query=query))
        # In this case a HTTPException(404) will have been raised
        # if no results were found, so don't need to check for it
        response = schemas.StoreResponse(results=results)
        logger.info("Returning: %s", response)
        return response

    assert_never(None)  # type: ignore
