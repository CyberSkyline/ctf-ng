"""
Contains the business logic to query
and retrieve a list of all events with their stats.
"""

from typing import Any

from ..models.Event import Event


def list_events() -> dict[str, Any]:
    """Gets all events with their team and member stats.

    Returns:
        dict: List of events with counts and total event count.
    """
    events_data = Event.get_events_with_stats()

    return {
        "events": events_data,
        "total_events": len(events_data),
    }
