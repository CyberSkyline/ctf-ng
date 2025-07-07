"""
Contains the business logic for updating an existing event's properties.
"""

from flask import g
from typing import Any
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from ...core import ValidationError
from ...core.utils import build_conditional_update_data
from ...core.validation import validate_unique_name
from ..models.Event import Event


def update_event(
    event_id: int,
    name: str | None = None,
    description: str | None = None,
    max_team_size: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    locked: bool | None = None,
) -> dict[str, Any]:
    """Updates an existing event with the provided data.

    Returns:
        dict: Updated event data
    """
    event = g.event

    if name:
        validate_unique_name(Event, name, current_object=event)

    update_data = build_conditional_update_data(
        event,
        name=(name, name and name != event.name),
        description=(description, description is not None),
        max_team_size=(
            max_team_size,
            max_team_size is not None and max_team_size != event.max_team_size,
        ),
        start_time=(start_time, start_time is not None),
        end_time=(end_time, end_time is not None),
        locked=(locked, locked is not None),
    )

    if not update_data:
        return event

    try:
        event.update_event(**update_data)
    except IntegrityError as e:
        raise ValidationError(f"Event update failed due to constraint violation: {str(e)}")

    return {"event": event}
