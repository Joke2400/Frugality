from fastapi import APIRouter


router = APIRouter()


@router.get("/stores/")
async def store_query(string: str):
    return string


@router.get("/stores/{store_id}")
async def get_store_by_id(store_id: int):
    return store_id
