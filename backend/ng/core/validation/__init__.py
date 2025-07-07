"""
Validation package for CTF-NG.
"""

from ..utils.validator import (
    BaseValidator,
    ValidationErrorMessages,
)
from .business_rules import (
    validate_unique_name,
    validate_team_capacity,
    validate_update_has_fields,
    validate_event_locked_state,
    validate_captain_leave_rules,
    validate_event_max_team_size,
    validate_ticket_reply_allowed,
    validate_event_timing,
)

from .team import (
    validate_team_leave,
    validate_team_update,
    validate_team_creation,
    validate_team_join_by_code,
    validate_captain_assignment,
)

from .support import (
    validate_ticket_creation,
    validate_ticket_message,
    validate_ticket_update,
    validate_tag_creation,
    validate_tag_update,
    validate_ticket_assignment,
    validate_ticket_filters,
    validate_ticket_tags_update,
)
from .event_registration import (
    validate_event_registration_creation,
    validate_join_event,
)

__all__ = [
    "BaseValidator",
    "ValidationErrorMessages",
    "validate_captain_assignment",
    "validate_captain_leave_rules",
    "validate_tag_creation",
    "validate_tag_update",
    "validate_team_capacity",
    "validate_team_creation",
    "validate_team_join_by_code",
    "validate_team_leave",
    "validate_team_update",
    "validate_ticket_assignment",
    "validate_ticket_creation",
    "validate_ticket_filters",
    "validate_ticket_message",
    "validate_ticket_reply_allowed",
    "validate_ticket_update",
    "validate_unique_name",
    "validate_update_has_fields",
    "validate_event_timing",
    "validate_ticket_tags_update",
    "validate_event_registration_creation",
    "validate_join_event",
]
