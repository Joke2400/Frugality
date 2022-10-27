from utils import LoggerManager as lgm
import core.database_manager.sqlalchemy_classes as dbc


logger = lgm.get_logger(name=__name__, level=20, stream=True)


class DataManager:

    def __init__(self, db):
        self.db = db

    def start_db(self, reset=False):
        if reset:
            logger.info(
                "Reset flag is set to True, resetting database...")
            self.reset_db()
        else:
            logger.info("Starting database...")
            self.db.create_all()

    def reset_db(self):
        self.db.drop_all()
        logger.info("Dropped database tables.")
        self.db.create_all()
        chain_names = ["s-market", "prisma", "sale", "alepa", "abc"]
        for chain in chain_names:
            self.db.session.add(dbc.StoreChain(chain))
        self.db.session.commit()
        logger.info("Created database tables.")
