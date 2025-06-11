"""
/backend/ctfd/plugin/event/controllers/list_events.py
Contains the business logic to query and retrieve a list of all events with their stats.
"""

from typing import Any

from sqlalchemy import func
from CTFd.models import db

from ...utils.logger import get_logger
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ..models.Event import Event

logger = get_logger(__name__)


def list_events() -> dict[str, Any]:
    """Gets all events with their team and member stats.

    Returns:
        dict: Success status, list of events with counts, and total event count.
    """
    event_stats = (
        db.session.query(
            Event.id,
            Event.name,
            Event.description,
            Event.start_time,
            Event.end_time,
            Event.locked,
            func.count(Team.id.distinct()).label("team_count"),
            func.count(TeamMember.id).label("total_members"),
        )
        .outerjoin(Team, Event.id == Team.event_id)
        .outerjoin(TeamMember, Event.id == TeamMember.event_id)
        .group_by(
            Event.id,
            Event.name,
            Event.description,
            Event.start_time,
            Event.end_time,
            Event.locked,
        )
        .all()
    )

    events_data = [
        {
            "id": event_id,
            "name": name,
            "description": description,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "locked": locked,
            "team_count": team_count,
            "total_members": total_members,
        }
        for (
            event_id,
            name,
            description,
            start_time,
            end_time,
            locked,
            team_count,
            total_members,
        ) in event_stats
    ]

    logger.info(
        "Events listed successfully",
        extra={"context": {"total_events": len(events_data)}},
    )

    return {
        "success": True,
        "events": events_data,
        "total_events": len(events_data),
    }
