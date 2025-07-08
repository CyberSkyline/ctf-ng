"""
Allows a user to join a team using an invite code.
"""

from flask import g
from typing import Any

from ...core.utils import utc_now
from ...core import BusinessLogicError

from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole
from ...user.models.User import User

from ...core.validation import (
    validate_event_locked_state,
    validate_event_timing,
)


def join_team(user_id: int, invite_code: str) -> dict[str, Any]:
    """Join a team using invite code.
    Returns:

        TeamMember: The created team member object.
    """
    team = g.team
    event = g.event
    eligibility = g.user_eligibility

    validate_event_locked_state(event, "new team members")
    validate_event_timing(event)

    if team.locked:
        raise BusinessLogicError(f"Team '{team.name}' is locked and not accepting new members")

    if not eligibility["can_join"]:
        existing_team_name = eligibility.get("current_team_name", "Unknown")
        raise BusinessLogicError(f"User is already in team '{existing_team_name}' for this event")

    user = User.find_by_id(user_id)
    if not user:
        user = User.create_user(user_id, commit=False)

    role = TeamRole.MEMBER
    team_member = TeamMember.create_team_member(
        user_id=user_id,
        team_id=team.id,
        event_id=team.event_id,
        joined_at=utc_now(),
        role=role,
    )

    return {"team_member": team_member}
