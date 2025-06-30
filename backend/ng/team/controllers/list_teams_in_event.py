"""
Retrieves a list of all teams within a specific event.
"""

from typing import Any

from ...core import NotFoundError
from ..models.Team import Team


def list_teams_in_event(event_id: int) -> dict[str, Any]:
    """
    Gets all teams in an event.

    Returns:
        dict: Teams data for the event.

    """
    teams_data = Team.get_all_teams_in_event_for_public(event_id)

    if teams_data is None:
        raise NotFoundError(f"Event with ID {event_id} does not exist")

    return teams_data
