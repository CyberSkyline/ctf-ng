"""
Contains the business logic to query
and retrieve a list of all events with their stats.
"""

from ..models.Event import Event

def list_events() -> list[Event]:
    """Gets all events with their team and member stats.
    """
    return Event.get_all_events()
