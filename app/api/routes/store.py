"""API routes for store retrieval."""
from fastapi import APIRouter, HTTPException


from app.utils import exceptions
from app.core import search, config
from app.core.orm import schemas, models

router = APIRouter()
MAX_REQUESTS_PER_QUERY = int(config.parser["API"]["max_requests_per_query"])


@router.get("/stores/{store_name}", response_model=list[schemas.Store])
async def get_store_by_name(
        store_name: str
        ) -> list[models.Store] | list[schemas.StoreBase] | list:
    strategies = [search.DBStoreSearchStrategy(),
                  search.APIStoreSearchStrategy()]
    # Looping over strategies as the match-case syntax is the same for both
    while strategies:
        context = search.SearchContext(strategy=strategies.pop(0))
        match await context.execute(query=store_name.strip()):
            case [search.State.SUCCESS, list()] as result:
                return result[1]  # Return the retrieved items
            case [search.State.FAIL | search.State.NO_RESPONSE, list()]:
                if len(strategies) != 0:
                    continue  # Skip to the next strategy as this one failed.
                raise HTTPException(
                    detail="Unable to retrieve items.",
                    status_code=404)
            case [search.State.PARSE_ERROR, list()]:
                raise HTTPException(
                    detail="Can't parse results from external API response.",
                    status_code=500)
            case _ as data:
                raise exceptions.InvalidMatchCaseError(
                    f"Could not match value: {data} to a predefined case.")
    return []  # Linter appeasement procedure
