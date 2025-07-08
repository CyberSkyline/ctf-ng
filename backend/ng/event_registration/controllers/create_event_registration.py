"""
Creates event registration configuration.
"""

from datetime import datetime

from ...event.models.Event import Event
from ..models.EventRegistration import EventRegistration

def create_event_registration(
    event : Event,
    public: bool = False,
    reg_open: bool = True,
    reg_start_date: datetime | None = None,
    reg_end_date: datetime | None = None,
) -> EventRegistration:
    """Create a new event registration for the specified event.

    Returns:
        EventRegistration: The created event registration object
    """
    registration = EventRegistration.create_event_registration(
        event_id=event.id,
        public=public,
        reg_open=reg_open,
        reg_start_date=reg_start_date,
        reg_end_date=reg_end_date,
    )

    return registration
