"""
Creates demographic entries for users joining events.
"""

from typing import Any

from ..models.Demographic import Demographic
from ...core.utils import utc_now


def create_demographic(user_id: int, event_id: int) -> dict[str, Any]:
    """Create a demographic entry for a user in an event.

    Args:
        user_id: The user ID
        event_id: The event ID

    Returns:
        dict: Created demographic data
    """
    demographic = Demographic.create_demographic(
        user_id=user_id,
        event_id=event_id,
        reg_timestamp=utc_now(),
    )

    return {"demographic": demographic}
