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

    event_data = event.serialize()

    event_data["team_count"] = Team.count_by_event(event.id)
    event_data["total_members"] = TeamMember.count_by_event(event.id)

    return {"success": True, "event": event_data}
