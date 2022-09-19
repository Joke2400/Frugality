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


def configure_logger(name: str, level: int = logging.DEBUG,
                     log_to_stream: bool = False,
                     log_to_file: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter("(%(asctime)s) [%(name)s]: %(message)s",
                                  "%Y-%m-%d %H:%M:%S")
    if log_to_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if log_to_file:
        file_handler = logging.FileHandler(Paths.logs() / f"{name}.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def add_logging(func, logger: logging.Logger):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug(f"Function: {func.__name__} \
            Args: {args} Kwargs: {kwargs} \
            Result: {result}")
        return result
    return wrapper
