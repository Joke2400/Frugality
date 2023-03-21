
from .program_paths import Paths
from .logger_manager import LoggerManager
from .util_funcs import timer, regex_search, regex_findall

LoggerManager.configure(
    logs_path=Paths.logs(),
    keep_logs=False
)
