from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.orm import (
    schemas,
    crud,
    get_db
)
from app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=20, fh=10)
router = APIRouter()


@router.get("/stores/{store_id}")
async def get_store_by_id(store_id: int, db: Session = Depends(get_db)):
    """Route that returns a single store record by searching by its id."""
    logger.debug(
        "Received a query for a store. Store ID: %s", store_id)
    return crud.get_store(session=db, store_id=store_id)


@router.get("/stores/{string}")
async def get_store_by_name(store_name: str, db: Session = Depends(get_db)):
    """Route that returns a single store record by searching by its name."""
    logger.debug(
        "Received a query for a store. Store Name: %s", store_name)
    return "OK" # Temp
