"""Contains helpful classes/functions/tests."""

from .logging import LoggerManager
from .paths import Project

# Ensuring the first call to logger manager is done
# here so that the singleton's init gets configured
# before actually using this class for creating loggers.

# TODO: PLACE THIS CALL ELSEWHERE, to avoid executing code in module init
logger_manager = LoggerManager(
    log_path=Project.logs_dir_path(),
    purge_old_logs=True
)