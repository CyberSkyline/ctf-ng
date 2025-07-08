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
    load_ticket,
    load_team,
    load_event,
    load_user,
    load_tag,
    load_team_by_invite_code,
    load_target_member,
    load_associations_from_request,
    load_team_and_event,
    load_user_team_in_event,
    load_team_and_event_by_invite,
    load_user_teams,
    load_user_event_team_data,
    load_user_details,
    load_current_user_as_target,
    load_tags_from_request,
)

from .checks import (
    require_user_access,
    require_ticket_access,
    require_ticket_update,
    require_team_captain,
    check_team_join_eligibility,
    require_event_is_joinable,
    check_demographic_eligibility,
)


__all__ = [
    # Core Decorators
    "handle_exceptions",
    "api_endpoint",
    "user_endpoint",
    "admin_endpoint",
    "public_endpoint",
    # Resource & Data Loaders
    "load_ticket",
    "load_team",
    "load_event",
    "load_user",
    "load_tag",
    "load_team_by_invite_code",
    "load_team_and_event_by_invite",
    "load_target_member",
    "load_associations_from_request",
    "load_team_and_event",
    "load_user_team_in_event",
    "load_user_teams",
    "load_user_event_team_data",
    "load_user_details",
    "load_current_user_as_target",
    "load_tags_from_request",
    # Permission & Logic Checkers
    "require_user_access",
    "require_ticket_access",
    "require_ticket_update",
    "require_team_captain",
    "check_team_join_eligibility",
    "require_event_is_joinable",
    "check_demographic_eligibility",
]
