from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base

def set_url(user: str, password: str) -> None:
    url = f"postgresql://{user}:{password}@5432:5432/db"
    engine = create_engine(
        url
    )
    print(engine)