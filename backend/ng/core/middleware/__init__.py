"""
Middleware System for the CTF-NG plugin.

This package provides a suite of decorators to handle authentication,
resource loading, and permission checking for API endpoints.
"""

from .error_handler import handle_exceptions
from .auth import (
    api_endpoint,
    user_endpoint,
    admin_endpoint,
    public_endpoint,
)
from .resources import (
    load_target_member,
    load_user_team_in_event,
    load_user_teams,
    load_user_event_team_data,
    load_user_details,
    load_current_user_as_target,
    load_tags_from_request,
)

__all__ = [
    # Core Decorators
    "handle_exceptions",
    "api_endpoint",
    "user_endpoint",
    "admin_endpoint",
    "public_endpoint",
    # Resource & Data Loaders
    "load_target_member",
    "load_user_team_in_event",
    "load_user_teams",
    "load_user_event_team_data",
    "load_user_details",
    "load_current_user_as_target",
    "load_tags_from_request",
]
