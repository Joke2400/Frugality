from typing import Dict
from pathlib import Path
import logging
import os


class LoggerManager:
    """
    A manager that keeps track of loggers and ensures that all child
    loggers of the top-level-directory logger output to the directory logger.

    Logs folder path should be configured before use by running the
    'configure' classmethod. If this is not done, LoggerManager will
    create a new 'logs' directory in the current working directory.
    """
    directory_loggers: Dict[str, logging.Logger] = {}
    logs_path: Path | str = Path.cwd() / "logs"
    root_log_path: Path = Path.cwd() / "logs" / "root.log"
    keep_logs: bool = False
    basic_formatter = logging.Formatter(
        fmt="(%(asctime)s) [%(levelname)s] ['%(name)s']: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    @classmethod
    def configure(cls, logs_path: Path | str, keep_logs: bool = False):
        """
        Configure the LoggerManager with a logs folder path
        and optionally with whether or not you want to keep logs
        from previous runs.

        Creates a new 'logs' directory in the current working directory
        if the given path is of an invalid type.

        Logs are not kept by default.
        """

        if isinstance(keep_logs, bool):
            cls.keep_logs = keep_logs
        else:
            raise TypeError(
                "keep_logs needs to be of type: bool")
        try:
            cls.logs_path = Path(logs_path)
        except TypeError:
            cls.logs_path = Path.cwd() / "logs"
            try:
                os.mkdir(cls.logs_path)
            except PermissionError:
                raise PermissionError(
                    "Could not create logs folder in current directory")
            except FileExistsError:
                pass

        cls.root_log_path = cls._get_log_path(log_name="root.log")
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(cls.basic_formatter)

        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[sh])

        if not cls.keep_logs:
            cls._remove_log_file(path=cls.root_log_path)

        fh = logging.FileHandler(cls.root_log_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(cls.basic_formatter)
        logging.getLogger().addHandler(fh)

    @classmethod
    def get_logger(cls, name: str, level: int = logging.INFO,
                   fmt: str = None, datefmt: str = None,
                   stream: bool = False, file: bool = True) -> logging.Logger:
        """
        Returns a top-level-directory logger, or creates it if it does
        not exist. Passing in the result of a __name__ call returns
        the corresponding child logger if a top-level-directory logger
        already exists.
        """
        if isinstance(name, str):
            module_name = name.split(".")[0]  # Get name of top-level module
            if (module_name == "root" or module_name == ""):
                raise ValueError(
                    "Top-level module name cannot be 'root' or ''")
        else:
            raise TypeError("'name' attr must be of type: (str)")
        formatter = None
        if fmt is not None and datefmt is not None:
            formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

        try:
            # Get directory logger,
            logging.debug(
                f"Directory loggers: {cls.directory_loggers}")
            dir_logger = cls.directory_loggers[module_name]
            logging.debug(
                f"Searched for and found logger '{module_name}' " +
                "in loggers dict.")
            name = name.replace(f"{module_name}.", "")
            logging.debug(
                f"Creating new child of logger '{module_name}', " +
                f"with name: '{name}'")
            logger = dir_logger.getChild(name)
            logger.setLevel(logging.DEBUG)  # Base level is always debug.
            logging.debug(
                f"Created logger: '{logger.name}'\n")
            return logger

        except KeyError:
            logging.debug(
                f"Directory logger '{module_name}' " +
                "was not found in loggers dict.")
            logger = logging.getLogger(module_name)
            logger.setLevel(logging.DEBUG)  # Base level is always debug.
            logger.propagate = False
            cls._configure_logger(logger=logger, name=logger.name,
                                  level=level, formatter=formatter,
                                  stream=stream, file=file)
            cls.directory_loggers[logger.name] = logger
            logging.debug(
                f"Created directory logger: '{logger.name}'\n")
        return logger

    @classmethod
    def _configure_logger(cls, logger: logging.Logger, name: str,
                          level: int = logging.INFO,
                          formatter: logging.Formatter = None,
                          stream: bool = False, file: bool = True) -> None:
        """
        Configures the directory logger with stream and filehandlers 
        based on given boolean values.
        """
        if formatter is None:
            formatter = cls.basic_formatter
            logging.debug(
                f"Adding basic formatter to '{name}'.")
        else:
            logging.debug(
                f"Adding custom formatter to '{name}'.")

        if stream:
            sh = logging.StreamHandler()
            sh.setFormatter(formatter)
            sh.setLevel(level)  # Stream log level is always self.level
            logger.addHandler(sh)
            logging.debug(
                f"Added streamhandler to '{name}'.")

        if file:
            log_path = cls._get_log_path(log_name=f"{name}.log")
            if not cls.keep_logs:
                cls._remove_log_file(path=log_path)

            fh = logging.FileHandler(log_path)
            fh.setFormatter(formatter)
            fh.setLevel(logging.DEBUG)  # File log level is always debug
            logger.addHandler(fh)
            logging.debug(
                f"Added filehandler to '{name}'.")

    @classmethod
    def _get_log_path(cls, log_name: str):
        """
        Returns complete path to the log file for a given log name.
        """
        if isinstance(cls.logs_path, Path):
            log_path = cls.logs_path / log_name
        else:
            raise TypeError(
                "logs_path is not of instance: pathlib.Path")
        return log_path

    @classmethod
    def _remove_log_file(cls, path: Path, root=False):
        """
        Attempts to remove a log file at the given path,
        logs the result into the root logger
        """
        try:
            os.remove(path)
            logging.debug(
                f"Deleted log file at: '{path}'.")
        except FileNotFoundError:
            logging.debug(
                f"Log file was not found at: '{path}'.")
        except PermissionError:
            logging.debug(
                f"Permission denied for log file at: '{path}' " +
                " Unable to delete.")
