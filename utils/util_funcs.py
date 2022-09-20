from functools import wraps
from utils import Paths
import time
import logging


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
                     log_to_file: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter("(%(asctime)s) [%(name)s]: %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    logger.setLevel(level)
    if log_to_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)

    if log_to_file:
        file_handler = logging.FileHandler(Paths.logs() / f"{name}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger
