"""API routes for store retrieval."""
from typing import cast
from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException
)
from app.core import typedefs
from app.core.orm import schemas
from app.core.search.state import SearchState
from app.core.search.store_flow import (
    DBStoreSearchStrategy,
    APIStoreSearchStrategy
)
from app.core.search.context import SearchContext
from app.utils.logging import LoggerManager

router = APIRouter()
logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
DBResultT = typedefs.DBStoreSearchResult
APIResultT = typedefs.APIStoreSearchResult


@router.post("/stores/")
async def get_stores(
            query: schemas.StoreQuery,
            background_tasks: BackgroundTasks
        ) -> schemas.StoreResponse:
    """TODO: Redo docstring"""
    logger.info("Performing a new store search...")
    with SearchContext(
            background_tasks=background_tasks,
            strategy=DBStoreSearchStrategy()) as context:
        state, db_results = cast(
            DBResultT, await context.execute(user_query=query))
        if state is SearchState.SUCCESS:
            # Schema handles conversion: schemas.StoreDB -> schemas.Store
            response = schemas.StoreResponse(
                results=db_results)  # type: ignore
            logger.info("Returning response: %s", response)
            return response
    # relatively simple query so not combining any results
    with SearchContext(
            background_tasks=background_tasks,
            strategy=APIStoreSearchStrategy()) as context:
        state, api_results = cast(
            APIResultT, await context.execute(user_query=query))
        if state is SearchState.SUCCESS:
            response = schemas.StoreResponse(results=api_results)
            logger.info("Returning response: %s", response)
            return response
        raise HTTPException(
            detail="Could not fulfill user query.",
            status_code=404)