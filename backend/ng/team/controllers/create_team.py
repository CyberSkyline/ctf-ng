"""
Creates a new team in an event with the creator as captain.
"""

from flask import g
from typing import Any

from ...core import BusinessLogicError
from ...core.validation import (
    validate_unique_name,
    validate_event_locked_state,
    validate_event_timing,
)
from ..models.Team import Team
from ._generate_invite_code import _generate_invite_code


def create_team(
    name: str,
    event_id: int,
    creator_id: int,
    ranked: bool = False,
) -> dict[str, Any]:
    """Creates a new team in the event with the creator as captain.

    Returns:
        dict: Created team data
    """
    event = g.event
    eligibility = g.user_eligibility

    validate_event_locked_state(event, "new teams")
    validate_event_timing(event)

    if not eligibility["can_join"]:
        raise BusinessLogicError("You are already in a team for this event")

    validate_unique_name(
        Team,
        name,
        scope_field="event_id",
        scope_value=event_id,
        error_message=f"Team '{name}' already exists in this event",
    )

    invite_code = _generate_invite_code()

    success, result = Team.create_team_with_captain(
        name=name,
        event_id=event_id,
        creator_id=creator_id,
        invite_code=invite_code,
        ranked=ranked,
    )

    if not success:
        raise BusinessLogicError(result["error"])

    return {"team": result["team"]}
