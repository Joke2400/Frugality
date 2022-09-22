from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship, backref

import core

Base = core.process.db.Model


class StoreChain(Base):

    __tablename__ = "store_chains"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __init__(self, name):
        self.name = name


class Store(Base):

    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    chain_id = Column(Integer, ForeignKey("store_chains.id"))
    name = Column(String, unique=True)
    open_times = Column(String)
    date_added = Column(String)
    date_updated = Column(String)
    select = Column(String)

    chain = relationship("StoreChain", backref="stores")
    products = relationship("StoreProduct", back_populates="store")

    def __init__(self, chain, name, open_times,
                 date_added, date_updated, select):
        self.chain = chain
        self.name = name
        self.open_times = open_times
        self.date_added = date_added
        self.date_updated = date_updated
        self.select = select


class StoreLocation(Base):

    __tablename__ = "store_locations"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    formatted_address = Column(String, unique=True)
    lat = Column(String)
    lon = Column(String)
    maps_place_id = Column(String)
    maps_plus_code = Column(String)

    store = relationship("Store", backref=backref("location", uselist=False))

    def __init__(self, store, formatted_address,
                 lat, lon, maps_place_id, maps_plus_code):
        self.store = store
        self.formatted_address = formatted_address
        self.lat = lat
        self.lon = lon
        self.maps_place_id = maps_place_id
        self.maps_plus_code = maps_plus_code


class ProductCategory(Base):

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class Product(Base):

    __tablename__ = "products"

    ean = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String)
    subname = Column(String)
    quantity = Column(String)
    unit = Column(String)
    img = Column(String)

    stores = relationship("StoreProduct", back_populates="product")

    def __init__(self, name, subname, quantity, unit, img):
        self.name = name
        self.subname = subname
        self.quantity = quantity
        self.unit = unit
        self.img = img


class StoreProduct(Base):

    __tablename__ = "store_products"

    store_id = Column(ForeignKey("stores.id"), primary_key=True)
    product_ean = Column(ForeignKey("products.ean"), primary_key=True)
    price = Column(Numeric)
    unit_price = Column(String)
    shelf_name = Column(String)
    shelf_href = Column(String)

    store = relationship("Store", back_populates="products")
    product = relationship("Product", back_populates="stores")
