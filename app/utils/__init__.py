"""Contains helpful classes/functions/tests."""

from .logger_manager import LoggerManager
from .paths import ProjectPaths

# Ensuring the first call to logger manager is done
# here so that the singleton's init gets configured
# before actually using this class for creating loggers.
logger_manager = LoggerManager(
    log_path=ProjectPaths.logs_dir_path(),
    purge_old_logs=True
)

__all__ = ["LoggerManager", "ProjectPaths"]
