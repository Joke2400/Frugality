"""Contains the paths used in the project."""
import configparser
from pathlib import Path


class FrugalityPaths:
    """Paths for Frugality app."""

    _project_path = Path.cwd()
    _secret_key_path = None
    _google_key_path = None

    @classmethod
    def set_project_path(cls, path: Path) -> None:
        """Set class project path to the given Path object."""
        if isinstance(path, Path):
            cls._project_path = path

    @classmethod
    def set_secret_path(cls, path: Path) -> None:
        """Set class secret key path to the given Path object."""
        if isinstance(path, Path):
            cls._secret_key_path = path

    @classmethod
    def set_google_path(cls, path: Path) -> None:
        """Set class google key path to the given Path object."""
        if isinstance(path, Path):
            cls._google_key_path = path

    @classmethod
    def project_path(cls):
        """Return the project path."""
        return cls._project_path

    @classmethod
    def secret_path(cls):
        """Return the secret key path."""
        return cls._secret_key_path

    @classmethod
    def google_path(cls):
        """Return the google key path."""
        return cls._google_key_path

    @classmethod
    def data_path(cls):
        """Return the path to data directory."""
        return cls.project_path() / "data"

    @classmethod
    def database_path(cls):
        """Return the path to the database."""
        return cls.project_path() / cls.data_path() / "database.db"

    @classmethod
    def test_database_path(cls):
        """Return the path to the test database."""
        return cls.project_path() / cls.data_path() / "test_database.db"

    @classmethod
    def templates_path(cls):
        """Return the path to templates directory."""
        return cls.project_path() / cls.data_path() / "templates"

    @classmethod
    def static_path(cls):
        """Return the path to static directory."""
        return cls.project_path() / cls.data_path() / "static"

    @classmethod
    def logs_path(cls):
        """Return path to logs directory.

        If logs directory does not exist, create it.
        """
        logs_path = cls.project_path() / "data" / "logs"
        if not logs_path.is_dir():
            Path.mkdir(logs_path)
        return logs_path

    @classmethod
    def settings_path(cls):
        """Return the path to the settings file."""
        return cls.project_path() / cls.data_path() / "settings.cfg"


config = configparser.ConfigParser()
config.read(FrugalityPaths.settings_path())

FrugalityPaths.set_secret_path(Path(config["PATHS"]["secret_key"]))
FrugalityPaths.set_google_path(Path(config["PATHS"]["google_key"]))
