"""API routes for store retrieval."""
from typing import cast
from fastapi import (
    APIRouter,
    BackgroundTasks
)
from app.core.search.store_flow import (
    DBStoreSearchStrategy,
    APIStoreSearchStrategy
)
from app.core.search.context import SearchContext
from app.core.orm import schemas
from app.utils.util_funcs import assert_never
from app.utils.logging import LoggerManager


logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
resultT = list[schemas.Store] | list[schemas.StoreDB[schemas.ProductDataDB]]
router = APIRouter()
strategies = (
    DBStoreSearchStrategy,
    APIStoreSearchStrategy
)


@router.post("/stores/", response_model=schemas.StoreResponse)
async def get_stores(
            query: schemas.StoreQuery,
            background_tasks: BackgroundTasks
        ):
    """API endpoint for retrieving store queries.

    Searches prioritize the internal database and only
    upon a failed search is the external API used.

    Args:
        query (schemas.StoreQuery):
            Contains a store name or store id or both
            See schemas.StoreQuery.

        background_tasks (BackgroundTasks):
            Passed in by FastAPI in order to facilitate the
            running of background tasks.
    Raises:
        HTTPException 404:
            Raises 404 if no items are found in the response.

        HTTPException 500:
            Raises 500 if external API did not respond
            Also raised if the API response could not be parsed.
    Returns:
        schemas.StoreResponse:
            Contains a 'results' key with the retrieved results.
            See the schema definition for the response format.
    """
    logger.info("Received a new store query.")
    for strategy in strategies:
        with SearchContext(query=query, strategy=strategy(),
                           task=background_tasks) as context:
            result = await context.execute_strategy()
            # Continue onto next strategy if result is None, this indicates a fail
            # Will be improved later, SearchContext needs major changes first
            if result is None:
                continue
            response = schemas.StoreResponse(results=result)  # type: ignore
            logger.info("Returning: %s", response)
            return response
    # This code should never be reached, raises AssertionError
    assert_never(None)  # type: ignore
