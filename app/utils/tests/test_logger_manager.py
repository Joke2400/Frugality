import logging
from pathlib import Path

from app.utils import LoggerManager

custom_fmt = logging.Formatter(
    fmt="(%(asctime)s) [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")

log_folder_path = Path.cwd() / "app" / "data" / "logs"

custom_dir = Path.cwd() / "app"


def test_init_default():
    """Test log folder path"""
    manager = LoggerManager(
        log_path=log_folder_path)
    assert manager.log_path == log_folder_path
    assert manager.root_dir == Path.cwd()
    del manager


def test_init_custom_dir():
    """Test custom logger root directory path"""
    manager = LoggerManager(
        log_path=log_folder_path,
        root_dir=custom_dir)
    assert manager.root_dir == custom_dir
    assert manager.root_dir.name == custom_dir.name
    del manager
