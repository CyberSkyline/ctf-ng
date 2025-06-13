"""
/backend/ctfd/plugin/event/controllers/get_event_info.py
Contains the business logic to retrieve all details for a single event, including its teams.
"""

from typing import Any

from sqlalchemy import func
from CTFd.models import db

from ...utils.logger import get_logger
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ..models.Event import Event

logger = get_logger(__name__)


def get_event_info(event_id: int) -> dict[str, Any]:
    """Gets detailed info about a event including all its teams.

    Args:
        event_id (int): The event ID to get info for.

    Returns:
        dict: Success status, event details, and list of teams in the event.
    """

    event = Event.query.get(event_id)
    if not event:
        logger.warning(
            "Get event info failed - event not found",
            extra={"context": {"event_id": event_id}},
        )
        return {"success": False, "error": "Event not found."}

    # Single join query to get teams with member counts, avoids N+1 queries
    teams_with_counts = (
        db.session.query(
            Team.id,
            Team.name,
            Team.ranked,
            func.count(TeamMember.id).label("member_count"),
        )
        .outerjoin(TeamMember, Team.id == TeamMember.team_id)
        .filter(Team.event_id == event_id)
        .group_by(Team.id, Team.name, Team.ranked)
        .all()
    )

    total_members = TeamMember.query.filter_by(event_id=event_id).count()

    teams_data = [
        {
            "id": team_id,
            "name": name,
            "member_count": member_count,
            "max_team_size": event.max_team_size,
            "is_full": member_count >= event.max_team_size,
            "ranked": ranked,
        }
        for team_id, name, ranked, member_count in teams_with_counts
    ]

    event_data = {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "max_team_size": event.max_team_size,
        "start_time": event.start_time.isoformat() if event.start_time else None,
        "end_time": event.end_time.isoformat() if event.end_time else None,
        "locked": event.locked,
        "team_count": len(teams_data),
        "total_members": total_members,
    }

    logger.info(
        "Event info retrieved successfully",
        extra={
            "context": {
                "event_id": event_id,
                "event_name": event.name,
                "team_count": len(teams_data),
                "total_members": total_members,
            }
        },
    )

    return {"success": True, "event": event_data, "teams": teams_data}
