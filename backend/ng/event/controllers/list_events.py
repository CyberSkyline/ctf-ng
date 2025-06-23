"""
/backend/ng/event/controllers/list_events.py
Contains the business logic to query and retrieve a list of all events with their stats.
"""

from typing import Any

from ...core.utils.logger import get_logger
from ..models.Event import Event

logger = get_logger(__name__)


def list_events() -> dict[str, Any]:
    """Gets all events with their team and member stats.

    Returns:
        dict: Success status, list of events with counts, and total event count.
    """
    events_data = Event.get_events_with_stats()

    logger.info(
        "Events listed successfully",
        extra={"context": {"total_events": len(events_data)}},
    )

    return {
        "success": True,
        "events": events_data,
        "total_events": len(events_data),
    }
