"""Contains a utility that provides the relative paths to files"""
from pathlib import Path
from app.utils.exceptions import UnknownPathError


class Project:
    """Class that provides paths to files in the application."""
    # Class adds a little overhead on app start, but is quick to edit.

    @staticmethod
    def root_path() -> Path:
        "Path to backend root."
        if Path.cwd().name == 'backend':
            return Path.cwd()
        else:
            if Path.cwd().parts[-1] == 'Frugality':
                return Path.cwd() / "backend"
            else:
                raise UnknownPathError(
                    message="Cannot determine project root path.")

    # Main app directory
    @staticmethod
    def app_dir_path() -> Path:
        """Path to the 'app' directory."""
        if Path.cwd().name != 'backend':
            return Path.cwd() / "backend" / "app"
        else:
            return Path.cwd() / "app"

    # Main sub-directories ------------
    @classmethod
    def api_dir_path(cls) -> Path:
        """Path to the 'api' sub-directory."""
        return cls.app_dir_path() / "api"

    @classmethod
    def core_dir_path(cls) -> Path:
        """Path to the 'core' sub-directory."""
        return cls.app_dir_path() / "core"

    @classmethod
    def data_dir_path(cls) -> Path:
        """Path to the 'data' sub-directory."""
        return cls.app_dir_path() / "data"

    @classmethod
    def utils_dir_path(cls) -> Path:
        """Path to the 'utils' sub-directory."""
        return cls.app_dir_path() / "utils"
    # -----------------------------

    @classmethod
    def settings_path(cls) -> Path:
        """Path to the settings file."""
        return cls.data_dir_path() / "settings.cfg"

    @classmethod
    def logs_dir_path(cls) -> Path:
        """Path to the 'logs' directory."""
        return cls.data_dir_path() / "logs"

    @classmethod
    def graphql_path(cls) -> Path:
        """Path to the graphql file."""
        return cls.data_dir_path() / "graphql"
