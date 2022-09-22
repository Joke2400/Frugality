
from .program_paths import Paths
from .logger_manager import LoggerManager
from .util_funcs import timer

LoggerManager.configure(
    logs_path=Paths.logs(),
    keep_logs=False
)
