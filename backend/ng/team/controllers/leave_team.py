"""
Removes a user from their current team in an event.
"""

from flask import g
from typing import Any

from ...core import BusinessLogicError
from ...core.validation import (
    validate_event_locked_state,
    validate_captain_leave_rules,
    validate_event_timing,
)
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole


def leave_team() -> dict[str, Any]:
    """Removes a user from their current team in the event.

    Returns:
        dict: Confirmation message and former team name.
    """
    team_member = g.team_member
    team = g.team
    event = g.event

    validate_event_locked_state(event, "leaving teams")
    validate_event_timing(event)

    if team.locked:
        raise BusinessLogicError(f"Team '{team.name}' is locked and members cannot leave")

    validate_captain_leave_rules(team_member, team)

    if team_member.role == TeamRole.CAPTAIN:
        other_members_count = TeamMember.count_other_members_in_team(team.id, team_member.id)
        if other_members_count == 0:
            team_name = team.name
            team.disband_team()
            return {
                "message": f"You have left and disbanded '{team_name}' as you were the last member.",
                "team_disbanded": True,
            }

    team_name = team.name
    team_member.remove_team_member()

    return {
        "message": f"Successfully left team '{team_name}'",
        "former_team": team_name,
    }
