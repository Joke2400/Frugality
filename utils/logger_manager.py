from typing import Dict
from pathlib import Path
import logging
import os


class LoggerManager:
    """
    A manager that keeps track of loggers and ensures that all modules nested
    within a project-level directory output their logs to the same logger.
    Thus also ensuring all of the modules output to a shared .log file.
    (Which is named after the project-level directory)

    Logs folder path should be configured before use by running the
    'configure' classmethod. If this is not done, LoggerManager will
    create a new 'logs' directory in the current working directory.
    """
    loggers: Dict[str, logging.Logger] = {}
    basic_fmt = "(%(asctime)s) [%(levelname)s] [%(module)s]: %(message)s"
    basic_datefmt = "%Y-%m-%d %H:%M:%S"
    logs_path = None
    keep_logs = False
    root_log = None

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

        if isinstance(keep_logs, bool):
            cls.keep_logs = keep_logs
        else:
            raise TypeError(
                "keep_logs needs to be of type: bool")

        cls.root_log = cls._get_log_path(log_name="root.log")
        formatter = logging.Formatter(
            fmt=cls.basic_fmt, datefmt=cls.basic_datefmt)

        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(formatter)

        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[sh])

        if not cls.keep_logs:
            cls._remove_log_file(path=cls.root_log)

        fh = logging.FileHandler(cls.root_log)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logging.getLogger().addHandler(fh)

    @classmethod
    def get_logger(cls, name: str, level: int = logging.INFO,
                   stream: bool = False, file: bool = True) -> logging.Logger:
        """
        Returns a logging.Logger instance if it is present in the 'loggers'
        class dict. Otherwise it creates a new ModuleLogger instance, adds it
        to the class dict, then returns the newly created instance.
        """
        if isinstance(name, str):
            name = name.split(".")[0]  # Get name of first item in __name__
            if name == "root" or name == "":
                raise ValueError("Logger name cannot be 'root' or ''")
        else:
            raise TypeError("name must be of type: (str)")
        try:
            logger = cls.loggers[name]
            logging.debug(
                f"Searched for and found logger '{name}' in loggers dict.")
        except KeyError:
            logging.debug(
                f"Logger '{name}' was not found in loggers dict.")
            logger = cls._create_logger(name, level, stream, file)
            logging.debug(
                f"Current loggers: {cls.loggers}")
        return logger

    @classmethod
    def _create_logger(cls, name: str, level: int = logging.INFO,
                       stream: bool = False, file: bool = True
                       ) -> logging.Logger:
        """
        Creates a logging.Logger instance, then adds it to loggers
        class variable
        """
        logging.debug(
            f"Creating new logger '{name}', with level: '{level}'.")
        logger = logging.Logger(name=name)
        logger.setLevel(logging.DEBUG)  # Base level is always debug.
        cls._configure_logger(logger=logger, name=name, level=level,
                              stream=stream, file=file)
        cls.loggers[name] = logger
        logging.debug(
            f"Created logger: '{name}'\n")
        return logger

    @classmethod
    def _configure_logger(cls, logger: logging.Logger, name: str,
                          level: int = logging.INFO, stream: bool = False,
                          file: bool = True) -> None:
        """
        Configures the logger with stream and filehandlers based on
        given boolean values.
        """
        formatter = logging.Formatter(
            fmt=cls.basic_fmt, datefmt=cls.basic_datefmt)
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
