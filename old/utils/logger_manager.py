"""Contains a class to manage logging."""
import os
import logging
from pathlib import Path

from .project_paths import FrugalityPaths


class LoggerManager:
    """
    A manager that keeps track of loggers and ensures that all child
    loggers of the top-level-directory logger output to the directory logger.

    Logs folder path should be configured before use by running the
    'configure' classmethod. If this is not done, LoggerManager will
    create a new 'logs' directory in the current working directory.
    """
    directory_loggers: dict[str, logging.Logger] = {}
    logs_dir_path: Path = FrugalityPaths.logs_path()
    root_log_path: Path = FrugalityPaths.logs_path() / "root.log"
    keep_logs: bool = False
    configured: bool = False
    default_format = logging.Formatter(
        fmt="(%(asctime)s) [%(levelname)s] ['%(name)s']: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    @classmethod
    def configure_defaults(
            cls,
            logs_path: Path | str | None = None,
            keep_logs: bool = True):
        try:
            cls.keep_logs = bool(keep_logs)
        except ValueError:
            cls.keep_logs = True

        if logs_path:
            try:
                cls.logs_dir_path = Path(logs_path)
            except TypeError:
                cls.logs_dir_path = Path.cwd() / "logs"
        if not cls.logs_dir_path.exists():
            try:
                os.mkdir(cls.logs_dir_path)
            except PermissionError as err:
                logging.exception(err)

        if not cls.keep_logs:
            cls._remove_log_file(path=cls.root_log_path)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

        # create StreamHandler object for console output
        stream_h = logging.StreamHandler()
        stream_h.setLevel(logging.INFO)
        stream_h.setFormatter(cls.default_format)

        # create FileHandler object for file output
        file_h = logging.FileHandler(cls.root_log_path)
        file_h.setLevel(logging.DEBUG)
        file_h.setFormatter(cls.default_format)

        # add new handlers to root logger
        root_logger.addHandler(stream_h)
        root_logger.addHandler(file_h)
        cls.configured = True
        logging.debug("Configured root logger.")

    @classmethod
    def get_logger(cls, name: str,
                   formatter: logging.Formatter | None = None,
                   path: Path | str | None = None,
                   level: int = logging.INFO,
                   keep_logs: bool = False) -> logging.Logger:
        if formatter is None:
            formatter = cls.default_format
        if path is None:
            path = cls.logs_dir_path
        if not cls.configured:
            cls.configure_defaults(logs_path=path, keep_logs=keep_logs)
        try:
            dir_name = name.split(".")[0]  # Get name of top-level module
            if dir_name in (""):
                raise ValueError(
                    f"Top-Level module name was invalid. {dir_name}")
        except (ValueError, TypeError) as err:
            logging.debug(err)
            dir_name = "root"

        try:
            dir_logger = cls.directory_loggers[dir_name]
            logging.debug("Found directory logger: '%s'", dir_logger.name)
            return cls.create_child_logger(dir_logger=dir_logger,
                                           child_name=name)
        except KeyError:
            logging.debug("Directory logger '%s' not found.", dir_name)
            dir_logger = cls.create_dir_logger(
                dir_name=dir_name,
                formatter=formatter,
                level=level,
                stream=True)
            if len(name.split(".")) > 1:
                logging.debug(
                    "Creating child for newly created directory logger")
                return cls.create_child_logger(dir_logger=dir_logger,
                                               child_name=name)
            return dir_logger

    @classmethod
    def create_child_logger(cls, dir_logger: logging.Logger,
                            child_name: str) -> logging.Logger:
        """Create a child logger for the given directory logger."""
        name = child_name.replace(f"{dir_logger.name}.", "")
        child_logger = dir_logger.getChild(name)
        child_logger.setLevel(logging.DEBUG)
        logging.debug("Created logger: '%s'", child_logger.name)
        return child_logger

    @classmethod
    def create_dir_logger(cls, dir_name: str,
                          level: int = logging.INFO,
                          stream: bool = False,
                          formatter: logging.Formatter = None
                          ) -> logging.Logger:
        """Create a directory-level logger that logs to a file.

        Level and stream attributes only apply to logger streamhandler.
        If no formatter is provided, uses default formatting.
        """
        logger = logging.getLogger(dir_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        cls._configure_logger(logger=logger, formatter=formatter,
                              level=level, stream=stream)
        cls.directory_loggers[logger.name] = logger
        logging.debug("Created new directory logger: '%s'", logger.name)
        return logger

    @classmethod
    def _configure_logger(cls, logger: logging.Logger,
                          formatter: logging.Formatter | None,
                          level: int = logging.INFO,
                          stream: bool = False) -> None:
        """Configure logger handlers based on given parameters.

        Streamhandler is added if 'stream' is set to True. 'level' attribute
        only applies to streamhandler. Filehandler is always set to debug.
        """
        if formatter is None:
            formatter = cls.default_format

        if stream:
            s_handler = logging.StreamHandler()
            s_handler.setFormatter(formatter)
            s_handler.setLevel(level)
            logger.addHandler(s_handler)
            logging.debug("Streamhandler added to: '%s'", logger.name)

        log_path = cls._get_log_path(name=f"{logger.name}.log")
        if log_path:
            if not cls.keep_logs:
                cls._remove_log_file(path=log_path)

            f_handler = logging.FileHandler(filename=log_path)
            f_handler.setFormatter(formatter)
            f_handler.setLevel(logging.DEBUG)
            logger.addHandler(f_handler)
        logging.debug("Configured logger: '%s'", logger.name)

    @classmethod
    def _get_log_path(cls, name: str) -> Path | None:
        """Create a complete path to log file in logs directory."""
        try:
            log_path = cls.logs_dir_path / name
        except (ValueError, TypeError) as err:
            logging.exception(err)
            return None
        return log_path

    @classmethod
    def _remove_log_file(cls, path: Path) -> bool:
        """Try to remove a log file at the given Path.

        If file was removed, or if file was not found, return True
        Return False if file could not be deleted due to an error.
        """
        try:
            path.unlink()
        except FileNotFoundError:
            logging.debug(
                "Could not find log file to remove: '%s'", path)
            return True
        except PermissionError:
            logging.debug(
                "(Permission denied) Could not remove log file: '%s'", path)
            return False
        except OSError as err:
            logging.exception(err)
            return False
        logging.debug(
            "Removed log file at: '%s'", path)
        return True
