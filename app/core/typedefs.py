"""Contains type definitions for easier re-use throughout the app."""
from typing import TypeVar
from app.core.orm import schemas, models

# ---- Grouped Aliases ----
ModelsAlias = models.Store | models.Product | models.ProductData
SchemaIn = schemas.Store | schemas.Product | schemas.ProductData
SchemaOut = schemas.StoreDB | schemas.ProductDB | schemas.ProductDataDB

SchemaInOrDict = SchemaIn | dict
SchemaOutOrDict = SchemaOut | dict

# ---- Bounded Typevars ----
OrmModelT = TypeVar("OrmModelT", bound=ModelsAlias)

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