"""API routes for product retrieval."""
from typing import cast
from fastapi import (
    APIRouter,
    BackgroundTasks
)
from backend.app.core.product_search import (
    DBProductSearchStrategy,
    APIProductSearchStrategy
)
from backend.app.core.typedefs import ProductSearchResult
from backend.app.core.search_context import SearchContext
from backend.app.core.orm import schemas
from backend.app.utils.util_funcs import assert_never
from backend.app.utils.logging import LoggerManager


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
            results: dict[int, list] = cast(
                dict[int, list], await context.execute_strategy())
            response = schemas.ProductResponse(results=results)  # type: ignore
            logger.info("Returning ProductResponse: %s", response)
            return response
    # This code should never be reached, raises AssertionError
    assert_never(None)  # type: ignore
