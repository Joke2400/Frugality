"""Contains type definitions for use throughout the app."""
from typing import TypeAlias
from app.core.orm import schemas, models
from app.core.search.state import SearchState

# These aliases are a fix that narrows down the type for Pylance.
# (Underlying schemas need to be defined using generics,
# as they're reliant on eachother & are defined in the same file)
StoreDB: TypeAlias = schemas.StoreDB[schemas.ProductDataDB]
ProductDB: TypeAlias = schemas.ProductDB[schemas.ProductDataDB]


OrmModel = models.Store | models.Product | models.ProductData
SchemaIn = schemas.Store | schemas.Product | schemas.ProductData
SchemaOut = StoreDB | ProductDB | schemas.ProductDataDB

# temporarily re-added
SchemaInOrDict = SchemaIn | dict

DBStoreSearchResult = \
    tuple[
        SearchState,
        list[StoreDB],
    ]


APIStoreSearchResult = \
    tuple[
        SearchState,
        list[schemas.Store],
    ]

StoreSearchResult = DBStoreSearchResult | APIStoreSearchResult

ProductTupleDB = \
    tuple[
        ProductDB,
        schemas.ProductDataDB
    ]

ProductTupleAPI = \
    tuple[
        schemas.Product,
        schemas.ProductData
    ]

DBProductResultItem = \
    tuple[
        dict[str, str | int | SearchState],
        list[ProductTupleDB]
    ]

APIProductResultItem = \
    tuple[
        dict[str, str | int | SearchState],
        list[ProductTupleAPI]
    ]

DBProductSearchResult = \
    tuple[
        SearchState,
        dict[
            int,
            list[DBProductResultItem]
        ]
    ] | tuple[
        SearchState,
        dict[
            int,
            list[DBProductResultItem]
        ],
        list[dict[str, str | int | SearchState]]
    ]


APIProductSearchResult = \
    tuple[
        SearchState,
        dict[
            int,
            list[APIProductResultItem]
        ],
    ]

ProductSearchResult = DBProductSearchResult | APIProductSearchResult
