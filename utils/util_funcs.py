from functools import wraps
from utils import Paths
import time
import logging
import os


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        print(f"Function: {func.__name__} Took {elapsed:.4f} second(s)")
        return result
    return wrapper


def configure_logger(name: str, level: int = logging.INFO,
                     log_to_stream: bool = False,
                     log_to_file: bool = True,
                     keep_previous: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        fmt="(%(asctime)s) [%(levelname)s] [%(filename)s] " +
        "{%(funcName)s}: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    logger.setLevel(logging.DEBUG)
    if log_to_stream:
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(level)
        logger.addHandler(sh)

    if log_to_file:
        log_path = Paths.logs() / f"{name}.log"

        if not keep_previous:
            result = None
            try:
                os.remove(log_path)
                result = f"Deleted log file at: \n\t{log_path}."
            except FileNotFoundError:
                result = f"Log file was not found at: \n\t{log_path}."
            except PermissionError:
                result = "Permission denied for log file at:" + \
                    f"\n\t{log_path}" + \
                    "\n\t(This might be due to Flask restarting in debug!)"
        fh = logging.FileHandler(log_path)
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)

        logger.addHandler(fh)
        if result:
            logger.debug(result)
    return logger
