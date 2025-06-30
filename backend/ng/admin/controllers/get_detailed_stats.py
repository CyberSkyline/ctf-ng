"""
Contains the business logic to query and create a statistics report.
"""

from typing import Any

from ...event.models.Event import Event
from ...team.models.Team import Team
from .get_data_counts import get_data_counts


def get_detailed_stats() -> dict[str, Any]:
    """Gets detailed stats including per event breakdowns and empty teams."""
    event_stats = Event.get_events_with_detailed_stats()
    empty_teams = Team.find_empty_teams()

    return {
        "overview": get_data_counts(),
        "events": event_stats,
        "empty_teams": empty_teams,
        "total_empty_teams": len(empty_teams),
    }
