from .sqlalchemy_db_classes import StoreChain

class DataManager:

    def __init__(self, db):
        self.db = db

    def start_db(self):
        self.db.create_all()
        chain_names = ["s-market", "prisma", "sale", "alepa", "abc"]
        for chain in chain_names:
            self.db.session.add(StoreChain(chain))
        self.db.session.commit()
