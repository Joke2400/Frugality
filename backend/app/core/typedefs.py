"""Contains type definitions for easier re-use throughout the app."""
from backend.app.core.orm import schemas, models
from backend.app.core.search_context import (
    APISearchState,
    DBSearchState,
)

# ---- Grouped Aliases ----
OrmModel = models.Store | models.Product | models.ProductData
SchemaIn = schemas.Store | schemas.Product | schemas.ProductData
SchemaOut = schemas.StoreDB | schemas.ProductDB | schemas.ProductDataDB

SchemaInOrDict = SchemaIn | dict
SchemaOutOrDict = SchemaOut | dict

QueryType = schemas.StoreQuery | schemas.ProductQuery
StoreResultT = tuple[APISearchState | DBSearchState,
                     list[schemas.Store | schemas.StoreDB]]
ProductResultT = \
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