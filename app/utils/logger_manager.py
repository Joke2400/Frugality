"""Contains a class for managing logging within the application."""
import os
import logging
from pathlib import Path
from typing_extensions import TypeAlias

Handler: TypeAlias = logging.StreamHandler | logging.FileHandler

#from app.utils import SingletonMeta


class LoggerManager:
    """Class for managing logging."""

    top_level_loggers: dict[str, logging.Logger] = {}
    default_format = logging.Formatter(
        fmt="(%(asctime)s) [%(levelname)s] ['%(name)s']: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    def __init__(self, log_path: Path | str,
                 purge_old_logs: bool = False) -> None:
        """Initialize an instance of LoggerManager.

        Args:
            log_path (Path | str):
                The path to the directory where the logs should be saved.
            purge_old_logs (bool, optional):
                Set to True if logs from previous runs should be purged.
                Defaults to False.
        """
        self.log_path = Path(log_path)
        if self.log_path.exists():
            if purge_old_logs:
                self.purge_logs(path=self.log_path)
        else:
            os.mkdir(self.log_path)
        self.root_logger = logging.getLogger()
        self.root_logger = self.create_logger(
            level=logging.DEBUG,
            sh=(logging.INFO, None),
            fh=(logging.DEBUG, None, self.log_path / "root.log"))


    def get_logger(self, name, level: int, sh: bool, fh: bool):
        print(name)
        return None

    @classmethod
    def create_logger(
            cls,
            level: int,
            parent: logging.Logger | None = None,
            name: str | None = None,
            sh: tuple[int,
                      logging.Formatter | None] | None = None,
            fh: tuple[int,
                      logging.Formatter | None,
                      Path] | None = None) -> logging.Logger:
        """TODO. Function also needs a refactor"""
        if parent is not None:
            if name is not None:
                parent.getChild(name)
            else:
                raise ValueError(
                    "The child logger needs a name suffix to be provided.")
        else:
            logger = logging.getLogger(name)
        logger.setLevel(level)
        if sh is not None:
            logger.addHandler(cls.configure_new_handler(
                level=sh[0], formatter=sh[1], handler_type="stream"))
        if fh is not None:
            logger.addHandler(cls.configure_new_handler(
                level=fh[0], formatter=fh[1],
                handler_type="stream", filename=fh[2]))
        return logger

    @classmethod
    def configure_new_handler(
            cls,
            level: int,
            formatter: logging.Formatter | None,
            handler_type: str = "stream",
            filename: Path | None = None) -> Handler:
        """Create and configure a new handler.

        Args:
            level (int):
                The level to set handler to.
            formatter (logging.Formatter | None):
                Add a custom formatter. Uses default format if not specified.
            handler_type (str):
                Must be set to either "stream" or "file".
                Determines which sort of handler is to be created.
            filename (Path | None):
                A path must be given if handler_type is set to 'file'.

        Raises:
            TypeError:
                Raised if a filehandler is being created and a path
                was not provided as the filename argument.
            ValueError:
                Raised if handler_type is not "file" or "stream".

        Returns:
            Handler: Returns either a Streamhandler or Filehandler
        """
        handler: logging.StreamHandler | logging.FileHandler
        if handler_type == "stream":
            handler = logging.StreamHandler()
        elif handler_type == "file":
            if filename is not None:
                handler = logging.FileHandler(filename=filename)
            raise TypeError(
                "A filehandler requires a filename to be provided.")
        else:
            raise ValueError(
                "Arg handler_type must be either 'stream' or 'file'")
        handler.setLevel(level)
        if formatter is not None:
            handler.setFormatter(formatter)
        else:
            handler.setFormatter(cls.default_format)
        return handler

    @staticmethod
    def purge_logs(path: Path) -> None:
        """Purge all files ending with '.log' at the given directory path."""
        try:
            if not os.path.isdir(path):
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


#logger_manager = LoggerManager(Path.cwd() / "app" / "data" / "logs")
#this_file_logger = logger_manager.get_logger(__name__, logging.DEBUG, True, True)
