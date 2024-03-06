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
from backend.app.core.typedefs import ProductResultT
from backend.app.core.search_context import SearchContext
from backend.app.core.orm import schemas
from backend.app.utils.util_funcs import assert_never

resultT = ProductResultT
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
    for strategy in strategies:
        with SearchContext(query=query, strategy=strategy(),
                           task=background_tasks) as context:
            results: dict[int, list] = cast(dict[int, list], await context.execute_strategy())
            r = schemas.ProductResponse(results=results)  # type: ignore
            return r
    # This code should never be reached, raises AssertionError
    assert_never(None)  # type: ignore
