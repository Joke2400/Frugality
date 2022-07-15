from abc import ABC, abstractmethod
from webscraper.data_manager_package.sqlalchemy_db_classes import StoreChain, Store, StoreLocation, Product, StoreProduct


class Command(ABC):

    def __init__(self, receiver, payload):
        self.receiver = receiver
        self.payload = payload

    @abstractmethod
    def execute(self):
        pass


class BasicRequest(Command):

    def __init__(self, receiver, payload, table):
        super().__init__(receiver, payload)
        self.table = table

    def execute(self):
        result = self.receiver.basic_query(
            table=self.table,
            payload=self.payload)
        return result

# DRY went out the window here :)
    # Gonna fix it later

class StoreRequest(Command):

    def __init__(self, receiver, payload):
        super().__init__(receiver, payload)
        self.table = Store

    def execute(self):
        result = self.receiver.basic_query(
            table=self.table,
            payload=self.payload)
        return result


class StoreChainRequest(Command):

    def __init__(self, receiver, payload):
        super().__init__(receiver, payload)
        self.table = StoreChain

    def execute(self):
        result = self.receiver.basic_query(
            table=self.table,
            payload=self.payload)
        return result


class StoreProductRequest(Command):

    def __init__(self, receiver, payload):
        super().__init__(receiver, payload)
        self.table = StoreProduct

    def execute(self):
        result = self.receiver.basic_query(
            table=self.table,
            payload=self.payload)
        return result


class DBAddStore(Command):

    def execute(self):
        if self.receiver.add_store(**self.payload):
            self.receiver.add_location(**self.payload)

class DBAddProduct(Command):

    def execute(self):
        self.receiver.add_product(**self.payload)
        self.receiver.add_store_product(**self.payload)
