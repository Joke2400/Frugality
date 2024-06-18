"""API routes for product retrieval."""
from typing import cast
from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException
)
from app.core import typedefs
from app.core.orm import schemas
from app.core.search.state import SearchState
from app.core.search.product_flow import (
    DBProductSearchStrategy,
    APIProductSearchStrategy
)
from app.core.search.context import SearchContext
from app.utils.logging import LoggerManager

router = APIRouter()
logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
DBResultT = typedefs.DBProductSearchResult
APIResultT = typedefs.APIProductSearchResult

# TODO: Implement request queue for product queries
# as it's likely to take a while if all products need
# to be queried from external API. Will need another
# route for retrieval of completed requests.


@router.post("/products/", response_model=schemas.ProductResponse)
async def get_products(
        query: schemas.ProductQuery, background_tasks: BackgroundTasks):
    """TODO: Docstring"""
    logger.info("Performing new product search...")
    with SearchContext(
            background_tasks=background_tasks,
            strategy=DBProductSearchStrategy()) as context:
        state, db_results = cast(
            DBResultT, await context.execute(
                user_query=query.get_as_dicts(), threshold=1))
        if state is SearchState.SUCCESS:
            # Schema handles conversion: schemas.ProductDB -> schemas.Product
            response = schemas.ProductResponse(
                results=db_results[0])  # type: ignore
            logger.info("Returning response: %s", response)
            return response
    api_query: list[typedefs.ProductQueryDictT] | schemas.ProductQuery
    if state is SearchState.PARTIAL_RESULT:
        api_query = db_results[1]
    else:
        # Run entire query
        api_query = query.get_as_dicts()
    with SearchContext(
            background_tasks=background_tasks,
            strategy=APIProductSearchStrategy()) as context:
        state, api_results = cast(
            APIResultT, await context.execute(user_query=api_query))
        if state is SearchState.SUCCESS:
            # TODO: COMBINE RESULTS FROM QUERIES BEFORE RETURNING!

            response = schemas.ProductResponse(results=api_results)
            logger.info("Returning response: %s", response)
            return response
        raise HTTPException(
            detail="Could not fulfill user query.",
            status_code=404)
