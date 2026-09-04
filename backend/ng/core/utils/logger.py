"""
Configures a JSON logger for machine readable app logging.
"""

import json
import logging
import os
import sys
import traceback
from datetime import UTC, datetime


def utc_now() -> datetime:
    """Get current UTC datetime. Replacement for deprecated datetime.utcnow()."""
    return datetime.now(UTC).replace(tzinfo=None)


PLUGIN_LOGGER_NAME = "ctfd_ng_plugin"
logger = logging.getLogger(PLUGIN_LOGGER_NAME)

# Frames kept from a traceback. A traceback is most of an entry's size, and the
# frames nearest the failure are the ones worth reading.
TRACEBACK_FRAME_LIMIT = 3


def format_traceback(exc_info=None, limit: int = TRACEBACK_FRAME_LIMIT) -> str:
    """
    Render an exception as a short traceback, most recent frame first.

    Args:
        exc_info: A `(type, value, traceback)` triple, as carried by a log
            record. Defaults to the exception currently being handled.
        limit: Frames to keep, counting back from the failure.

    Returns:
        The formatted frames followed by the exception line, or an empty
        string when there is no exception to report.
    """
    exc_type, exc, tb = exc_info or sys.exc_info()
    if tb is None:
        return ""

    # Most recent call first, limited to the frames nearest the failure
    frames = traceback.extract_tb(tb)[-limit:][::-1]

    return "".join(traceback.format_list(frames) + traceback.format_exception_only(exc_type, exc))


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": utc_now().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.filename,
            "function": record.funcName,
        }

        if hasattr(record, "context") and record.context:
            log_entry["context"] = record.context

        if hasattr(record, "trace") and record.trace:
            log_entry["trace"] = record.trace
        elif record.exc_info:
            # This formatter builds the entry field by field, so a traceback
            # passed as `exc_info=True` is dropped unless it is picked up here.
            log_entry["trace"] = format_traceback(record.exc_info)

        return json.dumps(log_entry)


def _configure_logger():
    """Configures the global plugin logger based on the execution environment."""

    if "pytest" in sys.modules:
        logger.addHandler(logging.NullHandler())
        logger.propagate = False
        return

    # Read the log level from the environment in docker-compose.yml
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()

    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    logger.propagate = False

    logger.info("Plugin logger configured with level: %s", log_level_str)


_configure_logger()


def get_logger(name: str) -> logging.Logger:
    """
    Returns a child logger of the globally configured plugin logger.
    This ensures all loggers inherit the same settings (level, formatter).
    """
    return logging.getLogger(f"{PLUGIN_LOGGER_NAME}.{name}")
