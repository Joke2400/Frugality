"""Contains a class for managing logging within the application."""
import os
import logging
from pathlib import Path
from typing_extensions import TypeAlias

from backend.app.utils.patterns import SingletonMeta, TreeNode

Handler: TypeAlias = logging.StreamHandler | logging.FileHandler


class LoggerManager(metaclass=SingletonMeta):
    """Class for managing logging in the application.

    Class uses a Singleton pattern. Configuration is to be set on
    first call, upon subsequent calls, .__init__() does not run again.

    Args:
        log_path (Path | str):
            The path to the directory where the logs should be stored.
            Cannot be set to None upon first call to Singleton.

        root_dir (Path | None):
            Define a folder that should be considered the project root.
            Defaults to the current working directory if set to None.

        purge_old_logs (bool):
            Set this to True if logs from previous runs should be purged.
            Defaults to False.

        default_format (logging.Formatter | None):
            Set a custom default format. If this is set to None,
            then the default format defined in the class is used instead.
    """
    tree: TreeNode
    loggers: list[logging.Logger] = []
    default_format = logging.Formatter(
        fmt="(%(asctime)s) [%(levelname)s] ['%(name)s']: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    def __init__(self, log_path: Path | str | None = None,
                 root_dir: Path | None = None,
                 purge_old_logs: bool = False,
                 default_format: logging.Formatter | None = None) -> None:
        """Initialize an instance of LoggerManager.

            Set the log path, root directory & default_format.
            Purge old logs if purge_old_logs is set to True
            Configure root logger with the right configuration.
            Initialize the logger tree with the root logger as the first node.
        """
        if default_format is not None:
            self.default_format = default_format
        if log_path is None:
            raise ValueError(
                "Log path must be provided on first call to class.")
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
        # quick and dirty fix to ensure root logger doesn't log to stream
        for i in self.root_logger.handlers:
            self.root_logger.removeHandler(i)
        config = self.create_config(
            logging.INFO, logging.DEBUG, self.default_format)
        config["file"]["filename"] = self.log_path / "root.log"
        self.root_logger = self.create_logger(
            name="root",
            level=logging.DEBUG,
            config=config)
        self.tree = TreeNode(
            data={"name": "root",
                  "logger": self.root_logger,
                  "path": self.root_dir})

    def get_logger(self, path: str,
                   sh: int, fh: int,
                   formatter: logging.Formatter | None = None,
                   name: str | None = None,
                   ) -> logging.Logger:
        """Get a new logger instance via the manager.

        Args:
            path (str):
                IMPORTANT: set this parameter to __name__.
                Path to the file that this call is coming from.

            sh (int):
                The level that the logger streamhandler should be set to.

            fh (int):
                The level that the logger filehandler should be set to.

            formatter (logging.Formatter | None):
                A custom formatter that the logger should use.
                Uses default_format defined in class if not provided.

            name (str | None, optional):
                TODO: IMPLEMENT THIS.

        Raises:
            ValueError:
                Raised if the path provided does not exist.

        Returns:
            logging.Logger: Returns a configured logger instance.
        """
        rel_path = Path(path.replace(".", "/") + ".py")
        if not (self.root_dir / rel_path).exists():
            raise ValueError(
                "Could not construct a valid logger path from path.")
        config = self.create_config(sh, fh, formatter)
        node = self.create_logger_tree(
            rel_path=rel_path, config=config)
        return node.data["logger"]

    def create_logger_tree(self, rel_path: Path, config: dict,
                           log_file_granularity: int = 2) -> TreeNode:
        """TODO: Proper docstring for this one"""
        node = self.tree
        for index, part_name in enumerate(rel_path.parts, start=1):
            # Check part_name doesn't exist in current node children.
            if len(children := (list(
                    filter(  # Linter sure likes to complain
                        lambda i: i.data["name"] == part_name, node.children
                        )))) == 1:
                # if len() = 1 -> Node with same name exists
                # -> Use the node in next loop.
                node = children[0]

            elif len(children) == 0:
                # if len() == 0 -> Node with name doesn't exist
                # -> Create that node -> Use the node in next loop
                rel_path_to_logger = Path(
                    "/".join(rel_path.parts[0:index]))
                abs_path_to_logger = self.root_dir / rel_path_to_logger
                child_config = config.copy()
                if part_name.endswith(".py"):
                    part_name = part_name.removesuffix(".py")

                if log_file_granularity >= index:
                    log_path = self.log_path / f"{part_name}.log"
                    child_config["file"]["filename"] = log_path
                else:
                    # Ensuring a filehandler does not get created
                    # so that logs don't get logged multiple times
                    del child_config["file"]

                new_child = TreeNode({
                    "name": part_name,
                    "logger": self.create_logger(
                        name=part_name,
                        level=logging.DEBUG,
                        parent=node.data["logger"],
                        config=child_config
                    ),
                    "path": abs_path_to_logger
                })
                node.add_child(new_child)
                node = new_child

            else:
                if len(children) != 0:
                    raise ValueError(
                        "Many nodes with same name, should not be possible.")
        return node

    def create_logger(
            self,
            name: str | None,
            level: int = 10,
            parent: logging.Logger | None = None,
            config: dict[str, dict] | None = None) -> logging.Logger:
        """Create a logger & configure it with the provided config.

        Args:
            name (str | None, optional):
                Name of the logger to create/modify.

            level (int, optional):
                The level that the logger (NOT THE HANDLERS!) should
                be set to. Defaults to 10, or equivalent to logging.DEBUG.

            parent (logging.Logger | None, optional):
                The parent of the logger to be created. If set to None,
                the root logger gets used instead. Defaults to None.

            config (dict[str, dict] | None, optional):
                The config dict used to configure the logger handlers.
                Defaults to None.

        Raises:
            ValueError:
                Raised if both: No parent given & no name given.

        Returns:
            logging.Logger: A configure logger instance.
        """
        if parent is None or name == "root":
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
            logger.addHandler(self.configure_handler(
                handler=logging.StreamHandler(),
                **sh))

        if (fh := config.get("file", None)) is not None:
            logger.addHandler(self.configure_handler(
                handler=logging.FileHandler(filename=fh.pop("filename")),
                **fh))
        self.loggers.append(logger)
        return logger

    @classmethod
    def configure_handler(
            cls,
            handler: Handler,
            level: int,
            formatter: logging.Formatter | None) -> Handler:
        """Configure a handler with a level and formatter.

        Args:
            handler (Handler):
                Handler instance to configure.
            level (int):
                Level to set handler instance to.
            formatter (logging.Formatter | None):
                Optional custom formatter that handler should use.

        Returns:
            Handler: Configured handler instance.
        """
        handler.setLevel(level)
        if formatter is not None:
            handler.setFormatter(formatter)
        else:
            handler.setFormatter(cls.default_format)
        return handler

    @staticmethod
    def create_config(sh: int, fh: int,
                      formatter: logging.Formatter | None) -> dict[str, dict]:
        """Create a config dict with levels/formatters for both handler types.
        Args:
            sh (int): The level to set the stream handler to.
            Should correspond to levels defined in the python logging module.

            fh (int): The level to set the file handler to.
            Should correspond to levels defined in the python logging module.

            formatter (logging.Formatter | None):
            Custom formatter to apply to both handlers.

        Returns:
            dict[str, dict]:
            Dict containing keys "stream" and "file". Each key contains the
            keys "level" and "formatter" with the values set.
        """
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
        """Purge all files ending with '.log' at the given directory path.

        Args:
            path (Path): Path to the logs folder.
        """
        try:
            if not path.is_dir():
                return None
        except ValueError as err:
            logging.error(err)
            return None

        for file in os.listdir(path):
            if file.endswith(".log"):
                try:
                    filepath = path / file
                    filepath.unlink()
                except PermissionError as err:
                    if file != "root":
                        logging.debug(err)
                finally:
                    logging.debug("Removed file at: '%s'", filepath)
        return None
