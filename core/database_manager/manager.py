import core.database_manager.sqlalchemy_db_classes as dbc


class DataManager:

    def __init__(self, db):
        self.db = db

    def start_db(self, reset=False):
        if reset:
            self.reset_db()
        else:
            self.db.create_all()

    def reset_db(self):
        self.db.drop_all()
        self.db.create_all()
        chain_names = ["s-market", "prisma", "sale", "alepa", "abc"]
        for chain in chain_names:
            self.db.session.add(dbc.StoreChain(chain))
        self.db.session.commit()
