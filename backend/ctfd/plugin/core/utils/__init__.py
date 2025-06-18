"""
Utility functions and decorators for common plugin functionality.
/backend/ctfd/plugin/core/utils/__init__.py
"""

from flask import g
from .logger import get_logger, logger
from .validation_framework import ValidationError, BaseValidator
from .domain_validators import (
    validate_team_creation,
    validate_team_update,
    validate_team_leave,
    validate_team_join_by_code,
    validate_captain_assignment,
    validate_event_creation,
    validate_event_update,
    validate_admin_reset,
    validate_admin_event_reset,
    validate_event_id_param,
)
from .data_conversion import rows_to_dicts, row_to_dict


def get_current_user_id():
    """Safely get the current user ID from Flask g context.

    Returns:
        int or None: User ID if available, None otherwise.
    """
    user = getattr(g, "user", None)
    return user.id if user else None


__all__ = [
    "get_logger",
    "logger",
    "get_current_user_id",
    "ValidationError",
    "BaseValidator",
    "validate_team_creation",
    "validate_team_update",
    "validate_team_leave",
    "validate_team_join_by_code",
    "validate_captain_assignment",
    "validate_event_creation",
    "validate_event_update",
    "validate_admin_reset",
    "validate_admin_event_reset",
    "validate_event_id_param",
    "rows_to_dicts",
    "row_to_dict",
]
