from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.utils import LoggerManager
from app.core import search
from app.core.orm import database, crud


logger = LoggerManager().get_logger(__name__, sh=20, fh=10)
router = APIRouter()


@router.get("/stores/{store_id}")
async def get_store_by_id(store_id: int):
    """Route that returns a single store record by searching by its id."""
    logger.debug(
        "Received a query for a store. Store ID: %s", store_id)
    return None
    return crud.get_store(session=db, store_id=store_id)
    "db: Session = Depends(database.get_db)"


@router.get("/stores/{string}")
async def get_store_by_name(store_name: str):
    """Route that returns a single store record by searching by its name."""
    logger.debug(
        "Received a query for a store. Store Name: %s", store_name)
    context = search.SearchContext(
        strategy=search.APISearchStrategy)
    result = context.execute()
    
