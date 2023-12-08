"""API routes for product retrieval."""
from fastapi import APIRouter, HTTPException

from app.core import search, config
from app.core.orm import schemas

router = APIRouter()
MAX_REQUESTS_PER_QUERY = int(config.parser["API"]["max_requests_per_query"])


@router.post("/products/")
async def product_query(query: schemas.ProductQuery):
    if MAX_REQUESTS_PER_QUERY < len(query.stores) * len(query.queries):
        raise HTTPException(
            detail="Too many item requests per query.",
            status_code=400)
    strategies = [search.APIProductSearchStrategy()]

    for _ in range(0, len(strategies)):
        context = search.SearchContext(strategy=strategies.pop(0))
        return await context.execute(query=query)
