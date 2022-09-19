import core.database_manager.sqlalchemy_db_classes as dbc
from utils import configure_logger

logger = configure_logger(name=__name__, level=20,
                          log_to_stream=True, log_to_file=True)


class DataManager:

    def __init__(self, db):
        self.db = db

    def start_db(self, reset=False):
        if reset:
            self.reset_db()
            logger.info("Resetting database to default.")
        else:
            self.db.create_all()
            logger.info("Starting database...")

    def reset_db(self):
        self.db.drop_all()
        logger.info("Dropped database tables.")
        self.db.create_all()
        chain_names = ["s-market", "prisma", "sale", "alepa", "abc"]
        for chain in chain_names:
            self.db.session.add(dbc.StoreChain(chain))
        self.db.session.commit()
        logger.info("Created new database tables.")
