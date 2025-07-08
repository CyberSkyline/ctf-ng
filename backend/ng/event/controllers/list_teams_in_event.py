"""
Retrieves a list of all teams within a specific event.
"""

from typing import Any

from ...core import NotFoundError
from ..models.Event import Event

def list_teams_in_event(event_id: int) -> dict[str, Any]:
    """
    Gets all teams in an event.

    Returns:
        dict: Teams data for the event.

    """
    event = Event.find_by_id(event_id)

    if not event:
        raise NotFoundError(f"Event with ID {event_id} does not exist")
    
    return event.get_all_teams()

