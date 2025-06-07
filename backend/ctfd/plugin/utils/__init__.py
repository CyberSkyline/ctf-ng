# /plugin/utils/__init__.py

from flask import g
from .decorators import authed_user_required, json_body_required
from .logger import get_logger, logger
from .validators import (
    validate_team_creation,
    validate_team_update,
    validate_team_join,
    validate_team_leave,
    validate_team_join_by_code,
    validate_captain_assignment,
    validate_world_creation,
    validate_world_update,
    validate_admin_reset,
    validate_admin_world_reset,
    validate_world_id_param,
)


def get_current_user_id():
    """Safely get the current user ID from Flask g context.

    Returns:
        int or None: User ID if available, None otherwise.
    """
    user = getattr(g, "user", None)
    return user.id if user else None


__all__ = [
    "authed_user_required",
    "json_body_required",
    "get_logger",
    "logger",
    "get_current_user_id",
    "validate_team_creation",
    "validate_team_update",
    "validate_team_join",
    "validate_team_leave",
    "validate_team_join_by_code",
    "validate_captain_assignment",
    "validate_world_creation",
    "validate_world_update",
    "validate_admin_reset",
    "validate_admin_world_reset",
    "validate_world_id_param",
]
