"""Contains type definitions for use throughout the app."""
from typing import TypeAlias
from app.core.orm import schemas, models
from app.core.search.state import SearchState

StoreDB: TypeAlias = schemas.StoreDB[schemas.ProductDataDB]
ProductDB: TypeAlias = schemas.ProductDB[schemas.ProductDataDB]


OrmModel = models.Store | models.Product | models.ProductData
SchemaIn = schemas.Store | schemas.Product | schemas.ProductData
SchemaOut = StoreDB | ProductDB | schemas.ProductDataDB

DBStoreSearchResult = \
    tuple[
        SearchState,
        list[StoreDB]
    ]

APIStoreSearchResult = \
    tuple[
        SearchState,
        list[schemas.Store]
    ]

StoreSearchResult = DBStoreSearchResult | APIStoreSearchResult

DBProductItem = \
    tuple[
        ProductDB,
        schemas.ProductDataDB
    ]

APIProductItem = \
    tuple[
        schemas.Product,
        schemas.ProductData
    ]

DBProductResultItem = \
    tuple[
        SearchState,
        dict[str, str | int],
        list[DBProductItem]
    ]

APIProductResultItem = \
    tuple[
        SearchState,
        dict[str, str | int],
        list[APIProductItem]
    ]

DBProductSearchResult = \
    tuple[
        SearchState,
        dict[
            int,
            list[DBProductResultItem]
        ]
    ]


APIProductSearchResult = \
    tuple[
        SearchState,
        dict[
            int,
            list[APIProductResultItem]
        ]
    ]

ProductSearchResult = DBProductSearchResult | APIProductSearchResult
