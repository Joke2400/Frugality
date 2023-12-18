"""Contains type definitions for easier re-use throughout the app."""
from typing import TypeVar
from app.core.orm import schemas, models

# ---- Grouped Aliases ----
ModelsAlias = models.Store | models.Product | models.ProductData
SchemasInAlias = schemas.Store | schemas.Product | schemas.ProductData
SchemasOutAlias = schemas.StoreDB | schemas.ProductDB | schemas.ProductDataDB

# ---- Bounded TypeVars ----
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