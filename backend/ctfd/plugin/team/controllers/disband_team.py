"""
/backend/ctfd/plugin/team/controllers/disband_team.py
Disbands a team and removes all its members.
"""

from typing import Any

from ...utils.logger import get_logger
from ..models.Team import Team
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole

logger = get_logger(__name__)


def disband_team(team_id: int, actor_id: int, is_admin: bool = False) -> dict[str, Any]:
    """Deletes a team and all its team members.

    Args:
        team_id (int): The team ID to disband.
        actor_id (int): The user ID doing the action.
        is_admin (bool, optional): Whether the actor is admin. Defaults to False.

    Returns:
        dict: Success status and confirmation message or error info.
    """
    team = Team.query.get(team_id)
    if not team:
        logger.warning(
            "Team disband failed - team not found",
            extra={"context": {"team_id": team_id, "actor_id": actor_id}},
        )
        return {"success": False, "error": "Team not found."}

    is_captain = TeamMember.query.filter_by(team_id=team_id, user_id=actor_id, role=TeamRole.CAPTAIN).first()

    if not is_admin and not is_captain:
        logger.warning(
            "Team disband failed - unauthorized user",
            extra={
                "context": {
                    "team_id": team_id,
                    "team_name": team.name,
                    "actor_id": actor_id,
                    "is_admin": is_admin,
                    "is_captain": bool(is_captain),
                }
            },
        )
        return {
            "success": False,
            "error": "You are not authorized to disband this team",
        }

    team_name = team.name
    event_id = team.event_id
    member_count = team.member_count

    team.disband_team()

    logger.info(
        "Team disbanded successfully",
        extra={
            "context": {
                "team_id": team_id,
                "team_name": team_name,
                "event_id": event_id,
                "actor_id": actor_id,
                "is_admin": is_admin,
                "member_count": member_count,
            }
        },
    )

    return {
        "success": True,
        "message": f"Team '{team_name}' has been disbanded.",
    }
