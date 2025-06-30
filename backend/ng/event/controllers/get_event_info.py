"""
Gets detailed info about an event.
"""

from flask import g
from typing import Any


def get_event_info(event_id: int) -> dict[str, Any]:
    """Gets detailed info about an event.

    Returns:
        dict: Event data with statistics.
    """
    event = g.event

    event_details = event.get_event_details_with_teams()

    return event_details
