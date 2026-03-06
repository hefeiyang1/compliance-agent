"""
Logging configuration for ComplianceAgent.
"""
import sys
from pathlib import Path
from typing import Any

from loguru import logger as _logger

from config.settings import settings


def setup_logging() -> None:
    """
    Configure application logging with Loguru.

    Sets up console and file logging with appropriate formats and rotation.
    """
    # Remove default handler
    _logger.remove()

    # Console handler with colors
    _logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=settings.log_level,
        colorize=True,
    )

    # General log file (rotating daily)
    log_file = settings.logs_dir / "compliance_{time:YYYY-MM-DD}.log"
    _logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )

    # Error log file (separate file for errors)
    error_log_file = settings.logs_dir / "errors_{time:YYYY-MM-DD}.log"
    _logger.add(
        error_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="1 day",
        retention="90 days",
        compression="zip",
        encoding="utf-8",
    )

    # JSON logs for machine processing (optional)
    if settings.debug:
        json_log_file = settings.logs_dir / "json_{time:YYYY-MM-DD}.log"
        _logger.add(
            json_log_file,
            format="{message}",
            level="INFO",
            rotation="1 day",
            retention="7 days",
            serialize=True,
            encoding="utf-8",
        )


class LoggerAdapter:
    """
    Logger adapter that adds context to log messages.

    Usage:
        logger = LoggerAdapter(__name__, context={"user_id": "123"})
        logger.info("User logged in")
    """

    def __init__(self, name: str, context: dict[str, Any] | None = None):
        """
        Initialize logger adapter.

        Args:
            name: Logger name (usually __name__)
            context: Additional context to include in all log messages
        """
        self._logger = _logger
        self._context = context or {}

    def _bind_context(self, **kwargs) -> Any:
        """Bind context to logger."""
        return self._logger.bind(**self._context, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._bind_context(**kwargs).debug(message)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._bind_context(**kwargs).info(message)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._bind_context(**kwargs).warning(message)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self._bind_context(**kwargs).error(message)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._bind_context(**kwargs).critical(message)

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self._bind_context(**kwargs).exception(message)


def get_logger(name: str, context: dict[str, Any] | None = None) -> LoggerAdapter:
    """
    Get a logger instance with optional context.

    Args:
        name: Logger name (usually __name__)
        context: Optional context dict to include in all log messages

    Returns:
        LoggerAdapter instance
    """
    return LoggerAdapter(name, context)


# Export logger
logger = _logger

# Auto-setup logging when module is imported
setup_logging()
