"""API routes for store retrieval."""
from typing import cast
from fastapi import APIRouter, HTTPException, BackgroundTasks


from backend.app.core.store_search import (
    DBStoreSearchStrategy,
    APIStoreSearchStrategy
)
from backend.app.core.search_context import (
    APISearchState,
    DBSearchState,
    SearchContext
)
from backend.app.core import config
from backend.app.core.orm import schemas
from backend.app.core.orm import models
from backend.app.core.typedefs import StoreResultT as ResultT
from backend.app.utils.util_funcs import assert_never

router = APIRouter()
MAX_REQUESTS_PER_QUERY = int(config.parser["API"]["max_requests_per_query"])
strategies = (
    DBStoreSearchStrategy,
    APIStoreSearchStrategy
)


@router.post("/stores/", response_model=list[schemas.Store])
async def get_stores(
            query: schemas.StoreQuery,
            background_tasks: BackgroundTasks
        ) -> list[models.Store] | list:
    """Perform a store search using the specified strategies.

    TODO: Improve docstring
    """
    for strategy in strategies:
        with SearchContext(query=query, strategy=strategy(),
                           task=background_tasks) as context:
            # Cast result of await to resultT so that mypy knows it's not 'Any'
            result: ResultT = cast(ResultT, await context.execute_strategy())
            match result:
                case [DBSearchState.SUCCESS |
                      APISearchState.SUCCESS, list()] as result:
                    return result[1]  # Return the successful result
                case [DBSearchState.FAIL, list()]:
                    continue  # Continue onto APISearchStrategy
                case [APISearchState.FAIL, list()]:
                    raise HTTPException(
                        detail="Could not find items from external API.",
                        status_code=404
                    )
                case [APISearchState.PARSE_ERROR, list()]:
                    raise HTTPException(
                        detail="Could not parse results from external API.",
                        status_code=500
                    )
                case [APISearchState.NO_RESPONSE, list()]:
                    raise HTTPException(
                        detail="Could not contact external API.",
                        status_code=500
                    )
                case _ as data:
                    assert_never(data)
    # This code should never be reached
    assert_never(None)  # type: ignore
