from fastapi import APIRouter

router = APIRouter()


class Counter:
    hits: int = 0

    @classmethod
    def increment(cls) -> int:
        cls.hits += 1
        return cls.hits


@router.get("/")
async def index():
    return f"The server is running. Hits: {Counter.increment()}."
