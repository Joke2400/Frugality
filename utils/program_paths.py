from pathlib import Path
from os import getlogin


class Paths:

    project = Path(f"C:\\Users\\{getlogin()}\\Desktop\\Frugality")
    google_key = Path(f"C:\\Users\\{getlogin()}\\Documents\\g_cloud_api.txt")
    secret_key = Path(f"C:\\Users\\{getlogin()}\\Documents\\secret.txt")

    @staticmethod
    def cwd():
        return Path.cwd()

    @staticmethod
    def home():
        return Path.home()

    @classmethod
    def database(cls):
        return cls.project / "data" / "database.db"

    @classmethod
    def test_database(cls):
        return cls.project / "data" / "test_database.db"

    @classmethod
    def templates(cls):
        return cls.project / "data" / "templates"

    @classmethod
    def static(cls):
        return cls.project / "data" / "static"

    @classmethod
    def logs(cls):
        return cls.project / "data" / "logs"

    @classmethod
    def settings(cls):
        raise NotImplementedError
