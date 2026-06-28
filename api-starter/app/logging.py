# Author: Ck.epsilon
"""Structured logging with loguru. Provides request-scoped loggers and slow-request detection."""

import sys
import time

from loguru import logger as _logger

# Remove default handler, add formatted stdout
_logger.remove()
_logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[request_id]:12}</cyan> | "
        "<level>{message}</level>"
    ),
    level="INFO",
    colorize=True,
)

# Default request_id for startup/shutdown (before middleware kicks in)
_logger.configure(extra={"request_id": "----------"})

logger = _logger


class RequestLogger:
    """Per-request logger wrapper that injects request_id automatically."""

    def __init__(self, request_id: str):
        self.request_id = request_id
        self._logger = _logger.bind(request_id=request_id)

    def info(self, msg: str, **kwargs):
        self._logger.info(msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        self._logger.warning(msg, **kwargs)

    def error(self, msg: str, **kwargs):
        self._logger.error(msg, **kwargs)

    def debug(self, msg: str, **kwargs):
        self._logger.debug(msg, **kwargs)
