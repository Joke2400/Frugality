"""Contains a class for managing logging within the application."""
import os
import logging
from pathlib import Path
from typing_extensions import TypeAlias

from app.utils import SingletonMeta, TreeNode

Handler: TypeAlias = logging.StreamHandler | logging.FileHandler


class LoggerManager(metaclass=SingletonMeta):
    """Class for managing logging."""

    tree: TreeNode
    default_format = logging.Formatter(
        fmt="(%(asctime)s) [%(levelname)s] ['%(name)s']: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    def __init__(self, log_path: Path | str,
                 root_dir: Path | None = None,
                 purge_old_logs: bool = False,
                 formatter: logging.Formatter | None = None) -> None:
        """Initialize an instance of LoggerManager.

        Args:
            log_path (Path | str):
                The path to the directory where the logs should be saved.
            purge_old_logs (bool, optional):
                Set to True if logs from previous runs should be purged.
                Defaults to False.
        """
        self.log_path: Path = Path(log_path)
        if root_dir is None:
            self.root_dir = Path.cwd()
        else:
            self.root_dir = root_dir
        if self.log_path.exists():
            if purge_old_logs:
                self.purge_logs(path=self.log_path)
        else:
            os.mkdir(self.log_path)
        self.root_logger = logging.getLogger()
        config = self.set_config(logging.DEBUG, logging.DEBUG, formatter)
        config["file"]["filename"] = self.log_path / "root.log"
        self.root_logger = self.create_logger(
            level=logging.DEBUG,
            config=config)
        self.tree = TreeNode(
            data={"name": "root",
                  "logger": self.root_logger,
                  "path": self.root_dir})

    def get_logger(self, path: str, sh: int = 0, fh: int = 0,
                   formatter: logging.Formatter | None = None
                   ) -> logging.Logger:
        """Get a new logger."""
        rel_path = Path(path.replace(".", "/") + ".py")
        abs_path = Path.cwd() / rel_path
        if not abs_path.exists():
            raise ValueError(
                "Could not construct a valid logger path from path.")
        config = self.set_config(sh, fh, formatter)
        node = self.tree
        for inx, filename in enumerate(rel_path.parts, start=1):
            # Funny one-liner | expecting only one result -> len() == 1
            if len(lst := ([i for i in node.children
                            if i.data["name"] == filename])) != 1:
                child_config = config.copy()
                log_path = self.log_path / f"{filename}.log"
                try:
                    child_config["file"]["filename"] = log_path
                except KeyError:
                    pass
                new_child = TreeNode({
                    "name": filename,
                    "logger": self.create_logger(
                        name=rel_path.name,
                        level=logging.DEBUG,
                        parent=node.data["logger"],
                        config=config
                    ),
                    "path": Path.cwd() / Path("".join(rel_path.parts[0:inx]))
                })
                node.add_child(new_child)
                node = new_child
                continue
            node = lst[0]

        return node.data["logger"]

    @classmethod
    def create_logger(
            cls,
            name: str | None = None,
            level: int = 10,
            parent: logging.Logger | None = None,
            config: dict[str, dict] | None = None) -> logging.Logger:
        """Create a new logger with optional handlers."""
        if parent is None:
            logger = logging.getLogger()  # Gets root logger
        else:
            if name is None:
                raise ValueError(
                    "The child logger needs a name suffix to be provided.")
            logger = parent.getChild(name)
        logger.setLevel(level)
        if config is None:  # Avoiding having a dict as a default value
            config = {}
        if (sh := config.get("stream", None)) is not None:
            logger.addHandler(cls.configure_handler(
                handler=logging.StreamHandler(),
                **sh))

        if (fh := config.get("file", None)) is not None:
            logger.addHandler(cls.configure_handler(
                handler=logging.FileHandler(filename=fh.pop("filename")),
                **fh))
        return logger

    @classmethod
    def configure_handler(
            cls,
            handler: Handler,
            level: int,
            formatter: logging.Formatter | None) -> Handler:
        """Configure a handler with a new level and formatter."""
        handler.setLevel(level)
        if formatter is not None:
            handler.setFormatter(formatter)
        else:
            handler.setFormatter(cls.default_format)
        return handler

    @staticmethod
    def set_config(sh: int, fh: int,
                   formatter: logging.Formatter | None) -> dict[str, dict]:
        """Set a config dict with levels/formatters for logger handlers."""
        config: dict[str, dict] = {}
        if sh != 0:
            config["stream"] = {
                "level": int(sh),
                "formatter": formatter
            }
        if fh != 0:
            config["file"] = {
                "level": int(fh),
                "formatter": formatter
            }
        return config

    @staticmethod
    def purge_logs(path: Path) -> None:
        """Purge all files ending with '.log' at the given directory path."""
        try:
            if not path.is_dir():
                return None
        except ValueError as err:
            logging.exception(err)
            return None

        for file in os.listdir(path):
            if file.endswith(".log"):
                try:
                    filepath = path / file
                    filepath.unlink()
                except PermissionError as err:
                    logging.exception(err)
                finally:
                    logging.debug("Removed file at: '%s'", filepath)
        return None
