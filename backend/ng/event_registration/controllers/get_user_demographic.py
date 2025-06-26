"""
Retrieves user demographic data for a specific event.
"""

from typing import Any
from ..models.Demographic import Demographic


def get_user_demographic(user_id: int, event_id: int) -> dict[str, Any]:
    """Get the demographic information for a user in a specific event.

    Args:
        user_id: The ID of the user
        event_id: The ID of the event

    Returns:
        dict: Status and demographic data
    """
    demographic = Demographic.find_by_user_and_event(user_id, event_id)

    if not demographic:
        return {"status": "not_registered"}

    return {"status": "registered", "details": {"user_id": demographic.user_id}}
