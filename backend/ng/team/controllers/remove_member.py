"""
/backend/ng/team/controllers/remove_member.py
Removes a member from a team with smart captain handling.
"""

from CTFd.models import db
from typing import Any
from datetime import datetime

from ...event.models.Event import Event
from ..models.Team import Team
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole
from ...core.utils.logger import get_logger

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
    team = Team.find_by_id(team_id)
    if not team:
        return {"success": False, "error": "Team not found."}

    event = Event.find_by_id(team.event_id)

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

    is_captain = TeamMember.find_captain_by_team_and_user(team_id, actor_id)

    if not is_admin and not is_captain:
        return {
            "success": False,
            "error": "You are not authorized to remove members",
        }

    team_member_to_remove = TeamMember.find_by_user_and_team(member_to_remove_id, team_id)

    if not team_member_to_remove:
        return {"success": False, "error": "User is not a member of this team"}

    if team_member_to_remove.user_id == actor_id:
        return {
            "success": False,
            "error": "Captains cannot remove themselves. Use the 'Leave Team' or 'Disband Team' feature.",
        }

    if team_member_to_remove.role == TeamRole.CAPTAIN:
        return _handle_captain_removal(team, team_member_to_remove, actor_id, is_admin)

    try:
        team_member_to_remove.remove_team_member(commit=False)
        team.update_invite_code(commit=False)
        db.session.commit()
        return {"success": True, "message": "Team member removed successfully."}
    except Exception as e:
        db.session.rollback()
        raise e


def _handle_captain_removal(team: Team, captain_to_remove: TeamMember, actor_id: int, is_admin: bool):
    """Smartly handles captain removal by either auto promoting or blocking."""

    remaining_members = TeamMember.find_remaining_members_for_captain_removal(team.id, captain_to_remove.id)

    if not remaining_members:
        captain_to_remove.remove_team_member()
        logger.info(f"Captain removed, team {team.id} is now empty.")
        return {"success": True, "message": "Captain removed. The team is now empty."}

    if is_admin:
        try:
            new_captain = remaining_members[0]
            new_captain.update_role(TeamRole.CAPTAIN, commit=False)
            captain_to_remove.remove_team_member(commit=False)
            team.update_invite_code(commit=False)
            db.session.commit()

            logger.info(
                f"Admin removed captain {captain_to_remove.user_id} from team {team.id}, auto-promoted {new_captain.user_id}."
            )
            return {
                "success": True,
                "message": f"Captain removed. User {new_captain.user_id} has been automatically promoted to captain.",
                "new_captain_id": new_captain.user_id,
            }
        except Exception as e:
            db.session.rollback()
            raise e
    else:
        return {
            "success": False,
            "error": "You cannot remove the captain while other members are on the team. Please transfer captaincy first.",
            "available_for_captaincy": [m.user_id for m in remaining_members],
        }
