"""
Creates a new team in an event with the creator as captain.
"""

from flask import g
from typing import Any

from ...core import BusinessLogicError
from ...core.validation import (
    validate_unique_name,
    validate_event_locked_state,
)
from ..models.Team import Team
from ._generate_invite_code import _generate_invite_code


def create_team(name: str, ranked: bool = False) -> dict[str, Any]:
    """Creates a new team in the event with the creator as captain.

    Returns:
        dict: Created team data
    """
    event = g.event
    user = g.user
    eligibility = g.user_eligibility

    validate_event_locked_state(event, "new teams")

    if not eligibility["can_join"]:
        raise BusinessLogicError("You are already in a team for this event.")

    validate_unique_name(Team, name, scope_field="event_id", scope_value=event.id)

    invite_code = _generate_invite_code()

    team = Team.create_team_with_captain(
        name=name,
        event_id=event.id,
        creator_id=user.id,
        invite_code=invite_code,
        ranked=ranked,
    )

    return team
