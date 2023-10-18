from fastapi import APIRouter


router = APIRouter()


@router.get("/products/")
async def product_query(string: str):
    return string


@router.get("/products/{product_id}")
async def get_product_by_id(product_id: int):
    return product_id