from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.orm import (
    schemas,
    crud,
    get_db
)

router = APIRouter()


@router.get("/debug/stores/create/{string}", response_model=schemas.StoreIn)
async def debug_store_create(string: str, db: Session = Depends(get_db)):
    """TEMPORARY DEBUG ROUTE: CREATE STORE RECORD"""
    from random import randint
    store = schemas.StoreIn(
        store_id=str(randint(0, 100000)),
        name=string,
        slug="test_slug",
        brand="test_brand"
    )
    return crud.create_store(db, store)
    # Issue with HTTPException, ctx manager gets closed too late on return
    # Might need to just not use the FastAPI Depends 


@router.get("/debug/stores/get/all", response_model=list[schemas.StoreOut])
async def debug_store_get_all(db: Session = Depends(get_db)):
    """TEMPORARY DEBUG ROUTE: GET ALL STORE RECORDS"""
    return crud.get_stores(db)
