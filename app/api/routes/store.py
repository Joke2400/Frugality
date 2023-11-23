from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.utils import LoggerManager
from app.core import search
from app.core.orm import database, crud, schemas


logger = LoggerManager().get_logger(__name__, sh=20, fh=10)
router = APIRouter()


@router.get("/stores/{store_name}")
async def get_store_by_name(store_name: str):
    """Route that returns a single store record by searching by its name."""
    logger.debug(
        "Received query for store by its name: %s", store_name)
    context = search.SearchContext(
        strategy=search.APIStoreNameSearchStrategy)
    d = {"store_name": store_name}
    query = schemas.StoreQuery(**d)
    return await context.execute(query=query)
