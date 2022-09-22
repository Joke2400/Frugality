from webscraper.data_manager_package.sqlalchemy_db_classes import (
    StoreLocation,
    StoreProduct,
    Product,
    Store,
)


def create_store(store_chain, **kwargs):
    store = Store(
        chain=store_chain,
        name=kwargs["name"],
        open_times=kwargs["open_times"],
        date_added=None,
        date_updated=None,
        select=kwargs["select"])
    return store


def create_location(store, **kwargs):
    location = StoreLocation(
        store=store,
        formatted_address=kwargs["address"],
        lat=None,
        lon=None,
        maps_place_id=None,
        maps_plus_code=None)
    return location


def create_product(**kwargs):
    product = Product(
        name=kwargs["name"],
        subname=kwargs["subname"],
        quantity=kwargs["quantity"],
        unit=kwargs["unit"],
        img=kwargs["img"])
    product.ean = kwargs["ean"]
    return product


def create_store_product(store, **kwargs):
    store_product = StoreProduct(
        store=store,
        store_id=store.id,
        price=kwargs["price"],
        unit_price=kwargs["unit_price"],
        shelf_name=kwargs["shelf_name"],
        shelf_href=kwargs["shelf_href"])
    return store_product
