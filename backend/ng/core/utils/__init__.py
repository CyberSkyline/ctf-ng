"""
Utility functions for common plugin functionality.
"""

from flask import g
from datetime import datetime, timezone

from .emitters import emit_event
from .logger import (
    get_logger,
    logger,
)
from .api import (
    success_response,
    error_response,
    serialize_model_for_api,
)
from .update import (
    build_update_data,
    build_conditional_update_data,
)


# --------Global get user_id ----------#
def get_current_user_id() -> int | None:
    """Safely get the current user ID from Flask g context.

    Returns:
        User ID if available, None otherwise.
    """
    user = getattr(g, "user", None)
    return user.id if user else None


# --------Global utc function ----------#
def utc_now() -> datetime:
    """
    Get current UTC datetime
    Replacement for deprecated datetime.utcnow()
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


__all__ = [
    "get_logger",
    "logger",
    "get_current_user_id",
    "utc_now",
    "serialize_model_for_api",
    "success_response",
    "error_response",
    "build_update_data",
    "build_conditional_update_data",
    "emit_event",
]
