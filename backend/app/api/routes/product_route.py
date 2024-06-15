"""API routes for product retrieval."""
from typing import cast
from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException
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


@router.post("/products/", response_model=schemas.ProductResponse)
async def get_products(
        query: schemas.ProductQuery, background_tasks: BackgroundTasks):
    """TODO: Docstring"""
    logger.info("Performing new ProductSearch...")
    raise HTTPException(
        detail="Route currently disabled",
        status_code=501
    )
    # Search the database
    with SearchContext(
            background_tasks=background_tasks,
            strategy=DBProductSearchStrategy()) as context:
        results: resultT = cast(
            resultT, await context.execute(user_query=query))
        print(results)

    with SearchContext(
            background_tasks=background_tasks,
            strategy=APIProductSearchStrategy()) as context:
        return None
