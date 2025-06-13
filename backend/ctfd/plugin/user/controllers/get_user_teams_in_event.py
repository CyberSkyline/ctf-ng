"""
/backend/ctfd/plugin/user/controllers/get_user_teams_in_event.py
Retrieves a user's team membership details within a specific event.
"""

from typing import Any

from ...utils.logger import get_logger
from ...event.models.Event import Event
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember

logger = get_logger(__name__)


def get_user_teams_in_event(user_id: int, event_id: int) -> dict[str, Any]:
    """Gets a user's team membership in a event.

    Args:
        user_id (int): The user ID.
        event_id (int): The event ID to check.

    Returns:
        dict: Success status, team info if user is in a team, or None if not.
    """

    event = Event.query.get(event_id)
    if not event:
        logger.warning(
            "Get user teams in event failed - event not found",
            extra={"context": {"user_id": user_id, "event_id": event_id}},
        )
        return {
            "success": False,
            "error": f"Event with ID {event_id} does not exist",
        }

    team_member = TeamMember.query.filter_by(user_id=user_id, event_id=event_id).first()

    if not team_member:
        logger.info(
            "User has no team membership in event",
            extra={
                "context": {
                    "user_id": user_id,
                    "event_id": event_id,
                    "event_name": event.name,
                }
            },
        )
        return {"success": True, "in_team": False, "team": None}

    team = Team.query.get(team_member.team_id)
    logger.info(
        "User team membership found in event",
        extra={
            "context": {
                "user_id": user_id,
                "event_id": event_id,
                "event_name": event.name,
                "team_id": team.id,
                "team_name": team.name,
                "role": team_member.role,
            }
        },
    )
    return {
        "success": True,
        "in_team": True,
        "team": {
            "id": team.id,
            "name": team.name,
            "member_count": team.member_count,
            "max_team_size": event.max_team_size,
            "is_full": team.member_count >= event.max_team_size,
            "ranked": team.ranked,
        },
        "team_member": {
            "joined_at": team_member.joined_at,
            "role": team_member.role,
        },
    }
