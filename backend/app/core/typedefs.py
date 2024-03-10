"""Contains type definitions for use throughout the app."""
from backend.app.core.orm import schemas, models
from backend.app.core.search_state import SearchState


OrmModel = models.Store | models.Product | models.ProductData
SchemaIn = schemas.Store | schemas.Product | schemas.ProductData
SchemaOut = schemas.StoreDB | schemas.ProductDB | schemas.ProductDataDB
SchemaInOrDict = SchemaIn | dict
SchemaOutOrDict = SchemaOut | dict

# SchemaIn defines the possible formats of records going into the database
# SchemaOut defines the possible formats of records coming out of the database

# i.e:
#       When creating a record:
#           SchemaIn -> OrmModel

#       When reading a record:
#           OrmModel -> SchemaOut


APIProductItem = \
    tuple[
        schemas.Product,
        schemas.ProductData
    ]

DBProductItem = \
    tuple[
        schemas.ProductDB,
        schemas.ProductDataDB
    ]

# This is the format that a product search strategy returns
ProductSearchResult = \
    tuple[
        SearchState,
        dict[
            int,
            list[
                tuple[
                    SearchState,
                    dict[str, str | int],
                    list[APIProductItem] | list[DBProductItem]
                ]
            ]
        ]
    ]

# This is the format that a store search strategy returns
StoreSearchResult = \
    tuple[
        SearchState,
        list[schemas.Store] | list[schemas.StoreDB]
    ]
