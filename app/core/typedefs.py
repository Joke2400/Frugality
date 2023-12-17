from typing import TypeVar
from app.core.orm import schemas, models

# ---- Pydantic ----
StoreT = schemas.StoreT
ProductT = schemas.ProductT
ProductDataT = schemas.ProductDataT

# ---- SQLAlchemy ----
StoreModelT = models.StoreModelT
ProductModelT = models.ProductModelT
ProductDataModelT = models.ProductDataModelT

# ---- Grouped Aliases ----
ModelsAlias = StoreModelT | ProductModelT | ProductDataModelT
SchemasInAlias = StoreT | ProductT | ProductDataT
SchemasOutAlias = schemas.StoreDB | schemas.ProductDB | schemas.ProductDataDB

# ---- TypeVars ----
OrmModelT = TypeVar("OrmModelT", bound=ModelsAlias)
PydanticSchemaInT = TypeVar("PydanticSchemaInT", bound=SchemasInAlias)
PydanticSchemaOutT = TypeVar("PydanticSchemaOutT", bound=SchemasOutAlias)


# ---- Function return signatures ----
ProductSearchResultT = \
    list[
        tuple[
            dict[str, str | int],
            list[
                tuple[
                    schemas.Product,
                    schemas.ProductData
                ]
            ]
        ]
    ]