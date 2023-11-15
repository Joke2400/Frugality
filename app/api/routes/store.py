from fastapi import APIRouter

from app.core.orm import schemas
from app.core.orm import crud

router = APIRouter()


@router.get("/stores/create/{string}")
async def store_create(string: str):
    store = schemas.StoreIn(
        store_id="12345678",
        name=string,
        slug="test_slug",
        brand="test_brand"
    )
    crud.create_store(store)
    return "OK"
    
@router.get("/stores/get/all")
async def store_query_all():
    stores = crud.get_stores()
    print(stores)
    
    return "OK"