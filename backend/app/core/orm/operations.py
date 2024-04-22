from typing import Type
from sqlalchemy import select
from pydantic import ValidationError
from backend.app.core.orm.database import SessionContext
from backend.app.core.orm import models, schemas, crud
from backend.app.core.typedefs import SchemaOut, SchemaIn, OrmModel
from backend.app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


def convert_to_model[ModelT: OrmModel](
        schema: SchemaIn, model: Type[ModelT]) -> ModelT | None:
    try:
        return model(**dict(schema))
    except ValueError as err:
        logger.debug(err)
    return None


def convert_to_schema[SchemaT: SchemaOut](
        model: OrmModel, schema: Type[SchemaT]) -> SchemaT | None:
    try:
        return schema.model_validate(model)
    except ValidationError as err:
        logger.debug(err)
    return None


def get_store_by_id(store_id: int, context: SessionContext) -> schemas.StoreDB | None:
    stmt = (
        select(models.Store)
        .where(models.Store.store_id == store_id)
    )
    with context:
        if (result := crud.select_one(stmt, session=context.session)) is None:
            return None
        item = convert_to_schema(
            model=result, schema=schemas.StoreDB)
    return item
