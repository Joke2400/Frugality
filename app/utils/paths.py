"""Utility that provides the relative paths to files"""
from pathlib import Path


class ProjectPaths:
    """Class that provides paths to files in the application."""

    @staticmethod
    def logs_dir_path():
        """The path to the logs directory."""
        return Path.cwd() / "app" / "data" / "logs"
