"""
Reusable validators for common resource validation patterns.
"""

from typing import Any
from ...team.models.enums import TeamRole
from ...team.models.TeamMember import TeamMember
from ..exceptions import ConflictError, ValidationError, BusinessLogicError
from ..utils import utc_now


# General
def validate_unique_name(
    model_class: type,
    new_name: str,
    current_object: object | None = None,
    scope_field: str | None = None,
    scope_value: Any | None = None,
    error_message: str | None = None,
) -> None:
    """Validates that a name is unique within a given scope."""
    if current_object and new_name == getattr(current_object, "name", None):
        return
    query = model_class.query.filter_by(name=new_name)
    if scope_field and scope_value is not None:
        query = query.filter(getattr(model_class, scope_field) == scope_value)
    if current_object:
        query = query.filter(model_class.id != current_object.id)
    existing = query.first()
    if existing:
        if not error_message:
            scope_text = f" in this {scope_field.replace('_id', '')}" if scope_field else ""
            error_message = f"Name '{new_name}' already exists{scope_text}"
        raise ConflictError(error_message)


def validate_update_has_fields(data, required_fields):
    """Business rule: updates must change something"""
    if not any(key in data for key in required_fields):
        raise ValidationError("At least one field must be provided for an update.")


# Team
def validate_team_capacity(team, event) -> None:
    """Check if team has room for new members"""
    if team.member_count >= event.max_team_size:
        raise BusinessLogicError(f"Team {team.name} is full ({team.member_count}/{event.max_team_size})")


def validate_captain_leave_rules(team_member, team) -> None:
    """Check if captain can leave team"""
    if team_member.role == TeamRole.CAPTAIN:
        other_members_count = TeamMember.count_other_members_in_team(team.id, team_member.id)
        if other_members_count > 0:
            raise BusinessLogicError("Captains cannot leave a team that has other members")

def validate_event_timing(event) -> None:
    """Check if operation is allowed based on event timing"""
    now = utc_now()

    if event.start_time and now < event.start_time:
        raise BusinessLogicError(f"Event '{event.name}' hasn't started yet")

    if event.end_time and now > event.end_time:
        raise BusinessLogicError(f"Event '{event.name}' has already ended")


# Support
def validate_ticket_reply_allowed(ticket, is_admin: bool) -> None:
    """Check if replies are allowed on this ticket"""
    if ticket.status == "closed" and not is_admin:
        raise BusinessLogicError("Cannot reply to a closed ticket")


# Events
def validate_event_locked_state(event, operation: str) -> None:
    """Check if operation is allowed on locked event"""
    if event.locked:
        raise BusinessLogicError(f"Event '{event.name}' is locked and not accepting {operation}")
