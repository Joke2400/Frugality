import logging
from pathlib import Path

from app.utils import LoggerManager
from app.utils.patterns import (
    SingletonMeta,
    find_neighbour_node
)

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
    SingletonMeta.debug_clear()
    del manager


def test_init_custom_directory():
    """Test init with custom directory path provided."""
    manager = LoggerManager(
        log_path=log_folder_path,
        root_dir=custom_dir)

    assert manager.log_path == log_folder_path
    assert manager.root_dir == custom_dir
    assert manager.tree.data["path"] == custom_dir

    # Reset the singleton
    SingletonMeta.debug_clear()
    del manager


def test_set_config():
    """Test set config method"""
    args = {"sh": 20, "fh": 0, "formatter": None}
    config = LoggerManager.set_config(**args)
    assert config.get("stream", None) is not None
    assert config.get("file", None) is None
    assert config["stream"]["formatter"] is None
    assert config["stream"]["level"] == 20


def test_configure_handler():
    """Test configure handler method."""
    handler = logging.StreamHandler()
    LoggerManager.configure_handler(handler, 10, None)
    assert handler.level == 10
    assert handler.formatter is LoggerManager.default_format
    del handler

    handler = logging.StreamHandler()
    LoggerManager.configure_handler(handler, 20, custom_fmt)
    assert handler.level == 20
    assert handler.formatter is custom_fmt


def test_create_root_logger():
    """Test create logger method - create root logger."""
    # Remove root handlers that have been created by pytest
    root = logging.getLogger()
    root.handlers = []

    manager = LoggerManager(
        log_path=log_folder_path,
        root_dir=custom_dir)

    # LoggerManager init automatically modifies the root logger
    logger = manager.tree.data["logger"]
    assert logger is logging.getLogger()
    assert logger.name == "root"
    assert logger.level == logging.DEBUG
    assert logger.parent is None

    assert logger.handlers[0].level == logging.DEBUG
    assert logger.handlers[1].level == logging.DEBUG

    assert logger.handlers[0].formatter is LoggerManager.default_format
    assert logger.handlers[1].formatter is LoggerManager.default_format

    # Reset the singleton
    SingletonMeta.debug_clear()
    del manager


def test_create_child_logger():
    """Test create logger method - create child logger."""
    # Remove root handlers that have been created by pytest
    root = logging.getLogger()
    root.handlers = []

    manager = LoggerManager(
        log_path=log_folder_path,
        root_dir=custom_dir)

    config = {
        "stream": {
            "level": 20,
            "formatter": None
        },
        "file": {
            "level": 10,
            "formatter": custom_fmt
        }
    }
    name = "custom_name"
    test_path = log_folder_path / "test.log"
    config["file"]["filename"] = test_path
    logger = manager.create_logger(
        name=name,
        level=logging.DEBUG,
        parent=manager.tree.data["logger"],  # == logging root logger
        config=config
    )
    assert logger.name == name
    assert logger.level == logging.DEBUG
    assert logger.parent is logging.getLogger()

    assert logger.handlers[0].level == logging.INFO
    assert logger.handlers[1].level == logging.DEBUG

    assert logger.handlers[0].formatter is LoggerManager.default_format
    assert logger.handlers[1].formatter is custom_fmt


def test_get_logger():
    pass
    """
    node = manager.tree
    for inx, part in enumerate(test_path.parts, start=0):
        if inx == 0:
            assert node.data["name"] == "root"
        else:
            assert node.data["name"] == part

        def wrap(comp):
            def validator(node):
                if node.data["name"] == comp:
                    return True
                return False
            return validator
        node = find_neighbour_node(node, wrap(part))
    """