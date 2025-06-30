"""
Removes a member from a team with captain handling.
"""

from flask import g
from typing import Any

from ...core import BusinessLogicError
from ...core.validation import (
    validate_event_locked_state,
    validate_event_timing,
)
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole


def remove_member(team_id: int, member_to_remove_id: int, actor_id: int, is_admin: bool = False) -> dict[str, Any]:
    """Removes a member from a team with auth checks.
    Returns:
        dict: Confirmation message
    """
    team = g.team
    event = g.event
    team_member_to_remove = g.target_member

    if not is_admin:
        validate_event_locked_state(event, "removing team members")
        validate_event_timing(event)

        if team.locked:
            raise BusinessLogicError(f"Team '{team.name}' is locked and members cannot be removed")

    if team_member_to_remove.user_id == actor_id:
        raise BusinessLogicError("Captains cannot remove themselves. Use the 'Leave Team' or 'Disband Team' feature.")

    if team_member_to_remove.role == TeamRole.CAPTAIN:
        return _handle_captain_removal(team, team_member_to_remove, actor_id, is_admin)

    team.remove_member_and_regenerate_code(team_member_to_remove.id)

    return {"message": "Team member removed successfully."}


def _handle_captain_removal(team, captain_to_remove: TeamMember, actor_id: int, is_admin: bool) -> dict[str, Any]:
    """Handles captain removal by either auto promoting or blocking."""
    remaining_members = TeamMember.find_remaining_members_for_captain_removal(team.id, captain_to_remove.id)

    if not remaining_members:
        captain_to_remove.remove_team_member()
        return {"message": "Captain removed. The team is now empty."}

    if is_admin:
        new_captain = remaining_members[0]
        team.remove_captain_and_promote(
            captain_to_remove_id=captain_to_remove.id,
            new_captain_user_id=new_captain.user_id,
        )

        return {
            "message": f"Captain removed. User {new_captain.user_id} has been automatically promoted to captain.",
            "new_captain_id": new_captain.user_id,
        }
    else:
        raise BusinessLogicError(
            "You cannot remove the captain while other members are on the team. Please transfer captaincy first."
        )
