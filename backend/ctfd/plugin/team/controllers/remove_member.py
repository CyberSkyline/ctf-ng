"""
/backend/ctfd/plugin/team/controllers/remove_member.py
Removes a member from a team with smart captain handling.
"""

from CTFd.models import db
from typing import Any
from datetime import datetime

from ...event.models.Event import Event
from ..models.Team import Team
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole
from ...utils.logger import get_logger

logger = get_logger(__name__)


def remove_member(team_id: int, member_to_remove_id: int, actor_id: int, is_admin: bool = False) -> dict[str, Any]:
    """Removes a member from a team with auth checks.

    Args:
        team_id (int): The team ID.
        member_to_remove_id (int): The member ID to remove.
        actor_id (int): The user ID doing the removal.
        is_admin (bool, optional): Whether the actor is admin. Defaults to False.

    Returns:
        dict: Success status and confirmation message or error info.
    """
    team = Team.query.get(team_id)
    if not team:
        return {"success": False, "error": "Team not found."}

    event = Event.query.get(team.event_id)

    if not is_admin:
        if event and (event.locked or (event.start_time and datetime.utcnow() >= event.start_time)):
            return {
                "success": False,
                "error": "Cannot remove members after the event has started or been locked.",
            }

        if team.locked:
            return {
                "success": False,
                "error": f"Team '{team.name}' is locked and members cannot be removed.",
            }

    is_captain = TeamMember.query.filter_by(team_id=team_id, user_id=actor_id, role=TeamRole.CAPTAIN).first()

    if not is_admin and not is_captain:
        return {
            "success": False,
            "error": "You are not authorized to remove members",
        }

    team_member_to_remove = TeamMember.query.filter_by(team_id=team_id, user_id=member_to_remove_id).first()

    if not team_member_to_remove:
        return {"success": False, "error": "User is not a member of this team"}

    if team_member_to_remove.user_id == actor_id:
        return {
            "success": False,
            "error": "Captains cannot remove themselves. Use the 'Leave Team' or 'Disband Team' feature.",
        }

    if team_member_to_remove.role == TeamRole.CAPTAIN:
        return _handle_captain_removal(team, team_member_to_remove, actor_id, is_admin)

    team_member_to_remove.remove_team_member(commit=False)
    team.update_invite_code(commit=True)
    return {"success": True, "message": "Team member removed successfully."}


def _handle_captain_removal(team: Team, captain_to_remove: TeamMember, actor_id: int, is_admin: bool):
    """Smartly handles captain removal by either auto promoting or blocking."""

    remaining_members = (
        TeamMember.query.filter(
            TeamMember.team_id == team.id,
            TeamMember.id != captain_to_remove.id,
            TeamMember.role == TeamRole.MEMBER,
        )
        .order_by(TeamMember.joined_at.asc())
        .all()
    )

    if not remaining_members:
        captain_to_remove.remove_team_member()
        logger.info(f"Captain removed, team {team.id} is now empty.")
        return {"success": True, "message": "Captain removed. The team is now empty."}

    if is_admin:
        new_captain = remaining_members[0]
        new_captain.update_role(TeamRole.CAPTAIN, commit=False)
        captain_to_remove.remove_team_member(commit=False)
        db.session.commit()

        logger.info(
            f"Admin removed captain {captain_to_remove.user_id} from team {team.id}, auto-promoted {new_captain.user_id}."
        )
        return {
            "success": True,
            "message": f"Captain removed. User {new_captain.user_id} has been automatically promoted to captain.",
            "new_captain_id": new_captain.user_id,
        }
    else:
        return {
            "success": False,
            "error": "You cannot remove the captain while other members are on the team. Please transfer captaincy first.",
            "available_for_captaincy": [m.user_id for m in remaining_members],
        }
