import logging
from pathlib import Path

from app.utils import LoggerManager
from app.utils import SingletonMeta

custom_fmt = logging.Formatter(
    fmt="(%(asctime)s) [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")

log_folder_path = Path.cwd() / "app" / "data" / "logs"

custom_dir = Path.cwd() / "app"


def test_init_default():
    """Test init with just a log_folder_path provided."""
    manager = LoggerManager(
        log_path=log_folder_path)

    assert manager.log_path == log_folder_path
    assert manager.root_dir == Path.cwd()
    assert manager.tree.data["path"] == Path.cwd()

    # Reset the singleton
    del manager
    SingletonMeta.debug_clear()


def test_init_custom_directory():
    """Test init with custom directory path provided."""
    manager = LoggerManager(
        log_path=log_folder_path,
        root_dir=custom_dir)

    assert manager.log_path == log_folder_path
    assert manager.root_dir == custom_dir
    assert manager.tree.data["path"] == custom_dir

    # Reset the singleton
    del manager
    SingletonMeta.debug_clear()
