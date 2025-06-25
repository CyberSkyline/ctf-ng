"""
Retrieves a list of all teams within a specific event (If needed).
"""

from typing import Any
from ..models.Team import Team


def list_teams_in_event(event_id: int) -> dict[str, Any]:
    """
    Gets all teams in an event.
    """

    teams_data = Team.get_all_teams_in_event_for_public(event_id)

    if teams_data is None:
        return {
            "success": False,
            "error": f"Event with ID {event_id} does not exist",
        }

    return {"success": True, **teams_data}
