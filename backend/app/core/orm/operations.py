
from backend.app.core.typedefs import SchemaOut, OrmModel


def convert_to_model[ModelT: OrmModel](model: ModelT) -> ModelT:
    pass

def convert_to_schema[SchemaT: SchemaOut](schema: SchemaT) -> SchemaT:
    pass