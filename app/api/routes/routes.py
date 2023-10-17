from fastapi import APIRouter, Response


router = APIRouter()


@router.get("/stores/")
async def store_query(string: str):
    return string


@router.get("/stores/{store_id}")
async def get_store_by_id(store_id: int):
    return store_id


@router.get("/products/")
async def product_query(string: str):
    return string


@router.get("/products/{product_id}")
async def get_product_by_id(product_id: int):
    return product_id