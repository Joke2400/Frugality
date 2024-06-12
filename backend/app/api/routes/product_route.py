"""API routes for product retrieval."""
from typing import cast
from fastapi import (
    APIRouter,
    BackgroundTasks
)
from app.core.search.product_flow import (
    DBProductSearchStrategy,
    APIProductSearchStrategy
)
from app.core.typedefs import ProductSearchResult
from app.core.search.context import SearchContext
from app.core.orm import schemas
from app.utils.util_funcs import assert_never
from app.utils.logging import LoggerManager


logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)

resultT = ProductSearchResult
router = APIRouter()
strategies = (
    DBProductSearchStrategy,
    APIProductSearchStrategy
)


@router.post("/products/")
async def get_products(
        query: schemas.ProductQuery, background_tasks: BackgroundTasks):
    """
    """
    logger.info("Received a new product query.")
    for strategy in strategies:
        with SearchContext(query=query, strategy=strategy(),
                           task=background_tasks) as context:
            result = await context.execute_strategy()
            if isinstance(result, list):
                # Continue onto next strategy if result is a list,
                # this indicates the need to do the next strategy
                # Will be improved later, SearchContext needs major changes first
                logger.info("Carryover requests: %s", result)
                continue
            response = schemas.ProductResponse(results=result)  # type: ignore
            logger.info("Returning ProductResponse: %s", response)
            return response
    # This code should never be reached, raises AssertionError
    assert_never(None)  # type: ignore
