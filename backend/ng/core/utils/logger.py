"""
Configures a JSON logger for machine readable app logging.
"""

import os
import json
import logging
import sys
from datetime import datetime, UTC


def utc_now() -> datetime:
    """Get current UTC datetime. Replacement for deprecated datetime.utcnow()."""
    return datetime.now(UTC).replace(tzinfo=None)


PLUGIN_LOGGER_NAME = "ctfd_ng_plugin"
logger = logging.getLogger(PLUGIN_LOGGER_NAME)


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
