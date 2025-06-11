"""
/backend/ctfd/plugin/user/controllers/get_user_teams.py
Retrieves all team memberships for a user across all events.
"""

from typing import Any

from sqlalchemy import func
from CTFd.models import db

from ...utils.logger import get_logger
from ...event.models.Event import Event
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ..models.User import User

logger = get_logger(__name__)


def get_user_teams(user_id: int) -> dict[str, Any]:
    """Gets all team members for a user across all events.

    Args:
        user_id (int): The user ID to get teams for.

    Returns:
        dict: Success status, list of teams with event info, and total count.
    """

    user = User.query.get(user_id)
    if not user:
        logger.warning(
            "Get user teams failed - user not found",
            extra={"context": {"user_id": user_id}},
        )
        return {"success": False, "error": "User not found in extended system"}

    # Single query with member count
    team_members_query = (
        db.session.query(
            TeamMember.joined_at,
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            Event.max_team_size.label("max_team_size"),
            Event.id.label("event_id"),
            Event.name.label("event_name"),
            func.count(TeamMember.id).over(partition_by=Team.id).label("team_member_count"),
        )
        .join(Team, TeamMember.team_id == Team.id)
        .join(Event, TeamMember.event_id == Event.id)
        .filter(TeamMember.user_id == user_id)
        .all()
    )

    teams_data = [
        {
            "team_id": team_member.team_id,
            "team_name": team_member.team_name,
            "event_id": team_member.event_id,
            "event_name": team_member.event_name,
            "joined_at": team_member.joined_at.isoformat() if team_member.joined_at else None,
            "max_team_size": team_member.max_team_size,
            "team_member_count": team_member.team_member_count,
        }
        for team_member in team_members_query
    ]

    logger.info(
        "User teams retrieved successfully",
        extra={
            "context": {
                "user_id": user_id,
                "total_teams": len(teams_data),
                "total_team_members": len(teams_data),
            }
        },
    )

    return {
        "success": True,
        "teams": teams_data,
        "total_teams": len(teams_data),
    }
