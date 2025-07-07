"""
Creates event registration configuration.
"""

from typing import Any
from flask import g
from datetime import datetime

from ..models.EventRegistration import EventRegistration


def create_event_registration(
    public: bool = False,
    reg_open: bool = True,
    reg_start_date: datetime | None = None,
    reg_end_date: datetime | None = None,
) -> dict[str, Any]:
    """Create a new event registration for the specified event.

    Returns:
        dict: Created event registration data
    """
    event = g.event

    registration = EventRegistration.create_event_registration(
        event_id=event.id,
        public=public,
        reg_open=reg_open,
        reg_start_date=reg_start_date,
        reg_end_date=reg_end_date,
    )

    return registration
