"""
Gets detailed info about an event.
"""

from typing import Any

def get_event_info(event: Any) -> dict[str, Any]:
    """Gets detailed info about an event.

    Returns:
        dict: Event data with statistics.
    """
    return event.get_event_details_with_teams()
