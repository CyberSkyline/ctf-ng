"""
Contains the business logic for creating and persisting a new event.
"""

from typing import Any
from datetime import datetime

from ...core.validation import validate_unique_name
from ..models.Event import Event


def create_event(
    name: str,
    description: str | None = None,
    max_team_size: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    locked: bool = False,
) -> dict[str, Any]:
    """Creates a new training event with the given config.

    Returns:
        dict: Created event data
    """

    validate_unique_name(Event, name, error_message=f"Event '{name}' already exists")

    event = Event.create_event(
        name=name,
        description=description,
        max_team_size=max_team_size,
        start_time=start_time,
        end_time=end_time,
        locked=locked,
    )

    return {"event": event}
