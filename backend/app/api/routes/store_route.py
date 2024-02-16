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
from backend.app.core.typedefs import StoreResultT as ResultT
from backend.app.utils.util_funcs import assert_never

router = APIRouter()
MAX_REQUESTS_PER_QUERY = int(config.parser["APP"]["max_requests_per_query"])
strategies = (
    DBStoreSearchStrategy,
    APIStoreSearchStrategy
)


@router.post("/stores/", response_model=list[schemas.Store])
async def get_stores(
            query: schemas.StoreQuery,
            background_tasks: BackgroundTasks
        ) -> list[schemas.Store]:
    """API endpoint for retrieving store queries.

    Searches prioritize the internal database and only
    upon a failed search is the external API used.

    Args:

        query (schemas.StoreQuery):
            A store query to use in the search.
            Contains a name or id or both, see schemas.StoreQuery.

        background_tasks (BackgroundTasks):
            Passed in by FastAPI in order to facilitate the running
            of background tasks.

    Raises:

        HTTPException 404:
            Raises exception 404 if no items are found in response.

        HTTPException 500:
            Raises exception 500 if external API did not respond
            or if API response could not be parsed.

    Returns:

        list[schemas.Store]:
            Return value is coerced into a list of type: schemas.Store.

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
    # This code should never be reached, raises AssertionError
    assert_never(None)  # type: ignore
