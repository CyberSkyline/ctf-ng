"""
/backend/ng/event/controllers/get_event_info.py
Contains the business logic to retrieve all details for a single event, including its teams.
"""

from typing import Any

from ...core.utils.logger import get_logger
from ..models.Event import Event

logger = get_logger(__name__)


def get_event_info(event_id: int) -> dict[str, Any]:
    """Gets detailed info about a event including all its teams.

    Args:
        event_id (int): The event ID to get info for.

    Returns:
        dict: Success status, event details, and list of teams in the event.
    """

    event = Event.find_by_id(event_id)
    if not event:
        logger.warning(
            "Get event info failed - event not found",
            extra={"context": {"event_id": event_id}},
        )
        return {"success": False, "error": "Event not found."}

    result = event.get_event_details_with_teams()
    event_data = result["event"]
    teams_data = result["teams"]

    logger.info(
        "Event info retrieved successfully",
        extra={
            "context": {
                "event_id": event_id,
                "event_name": event.name,
                "team_count": len(teams_data),
                "total_members": event_data["total_members"],
            }
        },
    )

    return {"success": True, "event": event_data, "teams": teams_data}
