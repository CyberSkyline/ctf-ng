"""
Gets detailed info about an event.
"""

from typing import Any

from ...core.utils.logger import get_logger
from ..models.Event import Event
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember

logger = get_logger(__name__)


def get_event_info(event_id: int) -> dict[str, Any]:
    """Gets detailed info about an event."""

    event = Event.find_by_id(event_id)
    if not event:
        logger.warning(
            "Get event info failed - event not found",
            extra={"context": {"event_id": event_id}},
        )
        return {"success": False, "error": "Event not found."}

    total_members = TeamMember.count_by_event(event.id)
    team_count = Team.count_by_event(event.id)

    event_data = {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "max_team_size": event.max_team_size,
        "start_time": event.start_time.isoformat() if event.start_time else None,
        "end_time": event.end_time.isoformat() if event.end_time else None,
        "locked": event.locked,
        "team_count": team_count,
        "total_members": total_members,
    }

    logger.info(
        "Event info retrieved successfully",
        extra={
            "context": {
                "event_id": event_id,
                "event_name": event.name,
                "team_count": team_count,
            }
        },
    )

    return {"success": True, "event": event_data}
