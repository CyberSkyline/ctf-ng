"""
/backend/ctfd/plugin/team/controllers/transfer_captaincy.py
Transfers captain role from current captain to another member.
"""

from CTFd.models import Users
from typing import Any

from ...utils.logger import get_logger
from ..models.Team import Team
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole

logger = get_logger(__name__)


def transfer_captaincy(team_id: int, new_captain_id: int, actor_id: int, is_admin: bool = False) -> dict[str, Any]:
    """Transfers captain role from current captain to another member.

    Args:
        team_id (int): The team ID.
        new_captain_id (int): The user ID who becomes captain.
        actor_id (int): The user ID doing the transfer.
        is_admin (bool, optional): Whether the actor is admin. Defaults to False.

    Returns:
        dict: Success status, new captain info, and message or error info.
    """
    team = Team.query.get(team_id)
    if not team:
        logger.warning(
            "Captain transfer failed - team not found",
            extra={
                "context": {
                    "team_id": team_id,
                    "actor_id": actor_id,
                    "new_captain_id": new_captain_id,
                }
            },
        )
        return {"success": False, "error": "Team not found."}

    is_current_captain = TeamMember.query.filter_by(team_id=team_id, user_id=actor_id, role=TeamRole.CAPTAIN).first()

    if not is_admin and not is_current_captain:
        logger.warning(
            "Captain transfer failed - unauthorized user",
            extra={
                "context": {
                    "team_id": team_id,
                    "team_name": team.name,
                    "actor_id": actor_id,
                    "new_captain_id": new_captain_id,
                    "is_admin": is_admin,
                    "is_current_captain": bool(is_current_captain),
                }
            },
        )
        return {
            "success": False,
            "error": "You are not authorized to assign captain",
        }

    new_captain_team_member = TeamMember.query.filter_by(user_id=new_captain_id, team_id=team_id).first()
    if not new_captain_team_member:
        logger.warning(
            "Captain transfer failed - new captain not a team member",
            extra={
                "context": {
                    "team_id": team_id,
                    "team_name": team.name,
                    "actor_id": actor_id,
                    "new_captain_id": new_captain_id,
                }
            },
        )
        return {"success": False, "error": "User is not a member of this team"}

    existing_captain = TeamMember.query.filter_by(team_id=team_id, role=TeamRole.CAPTAIN).first()
    old_captain_id = existing_captain.user_id if existing_captain else None

    if existing_captain:
        existing_captain.update_role(TeamRole.MEMBER, commit=False)

    new_captain_team_member.update_role(TeamRole.CAPTAIN, commit=True)

    # Get the new captain's name for user friendly message (optional)
    new_captain_user = Users.query.filter_by(id=new_captain_id).first()
    new_captain_name = new_captain_user.name if new_captain_user else f"User ID {new_captain_id}"

    logger.info(
        "Captain transferred successfully",
        extra={
            "context": {
                "team_id": team_id,
                "team_name": team.name,
                "old_captain_id": old_captain_id,
                "new_captain_id": new_captain_id,
                "new_captain_name": new_captain_name,
                "actor_id": actor_id,
                "is_admin": is_admin,
            }
        },
    )

    return {
        "success": True,
        "message": f"'{new_captain_name}' is now captain of '{team.name}'",
        "team_id": team.id,
        "captain_id": new_captain_id,
    }
