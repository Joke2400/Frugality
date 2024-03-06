"""Contains type definitions for easier re-use throughout the app."""
from backend.app.core.orm import schemas, models
from backend.app.core.search_state import SearchState

# ---- Grouped Aliases ----
OrmModel = models.Store | models.Product | models.ProductData
SchemaIn = schemas.Store | schemas.Product | schemas.ProductData
SchemaOut = schemas.StoreDB | schemas.ProductDB | schemas.ProductDataDB

SchemaInOrDict = SchemaIn | dict
SchemaOutOrDict = SchemaOut | dict

StoreResultT = \
    tuple[
        SearchState,
        list[schemas.Store] | list[schemas.StoreDB]
    ]

ProductResultT = \
    tuple[
        SearchState,
        dict[
            int,
            list[
                tuple[
                    SearchState,
                    dict[str, str | int],  # Contains original query info
                    list[
                        tuple[
                            schemas.Product | schemas.ProductDB,
                            schemas.ProductData | schemas.ProductDataDB
                        ]
                    ]
                ]
            ]
        ]
    ]
