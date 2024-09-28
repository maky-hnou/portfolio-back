"""Logging configuration and handler integration.

This module sets up logging for the application using the Loguru library.
It intercepts standard logging calls and redirects them to Loguru for better
formatting and management.

Dependencies:
    - logging: Standard library for logging in Python.
    - sys: Provides access to system-specific parameters and functions.
    - logger: Loguru's logging interface.

Classes:
    InterceptHandler: Custom logging handler that intercepts log records
                     and passes them to Loguru.
"""

import logging
import sys

from loguru import logger

from portfolio_backend.settings import settings


class InterceptHandler(logging.Handler):
    """Default handler from examples in loguru documentation.

    This handler intercepts all log requests and
    passes them to loguru.

    For more info see:
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        """Propagates logs to Loguru.

        Args:
            record (logging.LogRecord): The log record to propagate.
        """
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def configure_logging() -> None:  # pragma: no cover
    """Configure logging."""
    intercept_handler = InterceptHandler()

    logging.basicConfig(handlers=[intercept_handler], level=logging.NOTSET)

    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("uvicorn."):
            logging.getLogger(logger_name).handlers = []

    # change handler for default uvicorn logger
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]

    # set logs output, level and format
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level.value,
    )
