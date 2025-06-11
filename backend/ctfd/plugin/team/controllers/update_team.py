"""
/backend/ctfd/plugin/team/controllers/update_team.py
Updates team information with proper authorization checks.
"""

from typing import Any

from ...utils.logger import get_logger
from ..models.Team import Team
from ..models.TeamMember import TeamMember
from ..models.enums import TeamRole

logger = get_logger(__name__)


def update_team(
    team_id: int,
    actor_id: int,
    new_name: str | None = None,
    is_admin: bool = False,
) -> dict[str, Any]:
    """Updates team info with proper auth checks.

    Args:
        team_id (int): The team ID to update.
        actor_id (int): The user ID doing the update.
        new_name (str, optional): New team name if changing.
        is_admin (bool, optional): Whether the actor is admin. Defaults to False.

    Returns:
        dict: Success status, updated team info, and message or error info.
    """
    team = Team.query.get(team_id)
    if not team:
        logger.warning(
            "Team update failed - team not found",
            extra={"context": {"team_id": team_id, "actor_id": actor_id}},
        )
        return {"success": False, "error": "Team not found."}

    is_captain = TeamMember.query.filter_by(team_id=team_id, user_id=actor_id, role=TeamRole.CAPTAIN).first()

    if not is_admin and not is_captain:
        logger.warning(
            "Team update failed - unauthorized user",
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
            "error": "You are not authorized to edit this team",
        }

    changes_made = {}
    old_name = team.name

    if new_name is not None:
        if not new_name.strip():
            return {
                "success": False,
                "error": "Team name cannot be empty.",
            }

        existing_team = Team.query.filter(
            Team.event_id == team.event_id,
            Team.name == new_name,
            Team.id != team_id,
        ).first()
        if existing_team:
            logger.warning(
                "Team update failed - name already exists",
                extra={
                    "context": {
                        "team_id": team_id,
                        "old_name": team.name,
                        "new_name": new_name,
                        "event_id": team.event_id,
                        "existing_team_id": existing_team.id,
                        "actor_id": actor_id,
                    }
                },
            )
            return {
                "success": False,
                "error": f"A team with the name '{new_name}' already exists in this event.",
            }
        changes_made["name"] = {"old": old_name, "new": new_name}
        team.update_name(new_name, commit=True)

    logger.info(
        "Team updated successfully",
        extra={
            "context": {
                "team_id": team_id,
                "actor_id": actor_id,
                "is_admin": is_admin,
                "changes_made": changes_made,
                "event_id": team.event_id,
            }
        },
    )

    return {
        "success": True,
        "team": team,
        "message": "Team updated successfully",
    }
