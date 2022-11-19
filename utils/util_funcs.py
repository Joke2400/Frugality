from functools import wraps
import time


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        print(f"Function: {func.__name__}() Took {elapsed:.4f} second(s)")
        return result
    return wrapper
