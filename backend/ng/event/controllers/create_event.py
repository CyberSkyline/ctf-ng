"""
Contains the business logic for creating and persisting a new event.
"""

from datetime import datetime

from ..models.Event import Event


def create_event(
    name: str,
    description: str = "",
    max_team_size: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    locked: bool = False,
) -> Event:
    """Creates a new training event with the given config.

    Returns:
        Event: Created event instance
    """

    event = Event.create_event(
        name=name,
        description=description,
        max_team_size=max_team_size,
        start_time=start_time,
        end_time=end_time,
        locked=locked,
    )

    return event
