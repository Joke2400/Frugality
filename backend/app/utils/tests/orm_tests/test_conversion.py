from datetime import datetime
from backend.app.core.orm import schemas, models
from backend.app.core.orm.operations import convert_to_model, convert_to_schema
from backend.app.utils.util_funcs import log_test_name


@log_test_name
def test_convert_to_model_default():
    """Test the successful conversion of schema to model"""
    store = schemas.Store(
        store_name="Test Store",
        store_id=123,
        slug="test-store",
        brand=""
    )
    converted = convert_to_model(
        schema=store, model=models.Store)
    assert isinstance(converted, models.Store)


@log_test_name
def test_convert_to_schema_default():
    """Test the successful conversion of schema to model"""
    store = models.Store(
        id=1,
        store_id=123,
        store_name="Test Store",
        slug="test-store",
        brand="",
        timestamp=datetime.now()
    ) 
    # Timestamp and ID have to be manually added here
    # as the database usually handles that automatically
    converted = convert_to_schema(
        model=store, schema=schemas.StoreDB
    )
    assert isinstance(converted, schemas.StoreDB)
