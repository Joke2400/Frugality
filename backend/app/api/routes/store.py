"""API routes for store retrieval."""
from fastapi import APIRouter, HTTPException, BackgroundTasks

from backend.app.core import config
from backend.app.core import store_search
from backend.app.core import search_context as search
from backend.app.core.orm import schemas
from backend.app.core.orm import models
from backend.app.utils import exceptions

router = APIRouter()
MAX_REQUESTS_PER_QUERY = int(config.parser["API"]["max_requests_per_query"])


@router.get("/stores/{store_name}", response_model=list[schemas.Store])
async def get_store_by_name(
        store_name: str, background_tasks: BackgroundTasks
        ) -> list[models.Store] | list[schemas.StoreBase] | list:
    strategies = [store_search.DBStoreSearchStrategy(),
                  store_search.APIStoreSearchStrategy()]
    # Looping over strategies as the match-case syntax is the same for both
    while strategies:
        context = search.SearchContext(strategy=strategies.pop(0))
        match await context.execute(query=store_name.strip(),
                                    tasks=background_tasks):
            case [search.SearchState.SUCCESS, list()] as result:
                return result[1]  # Return the retrieved items
            case [search.SearchState.FAIL | search.SearchState.NO_RESPONSE,
                  list()]:
                if len(strategies) != 0:
                    continue  # Skip to the next strategy as this one failed.
                raise HTTPException(
                    detail="Unable to retrieve items.",
                    status_code=404)
            case [search.SearchState.PARSE_ERROR, list()]:
                raise HTTPException(
                    detail="Can't parse results from external API response.",
                    status_code=500)
            case _ as data:
                raise exceptions.InvalidMatchCaseError(
                    f"Could not match value: {data} to a predefined case.")
    return []  # Linter appeasement procedure
