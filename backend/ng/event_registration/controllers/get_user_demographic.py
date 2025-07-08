"""
Retrieves user demographic data for a specific event.
"""

from ..models.Demographic import Demographic
from ...event.models.Event import Event
from ...user.models.User import User

def get_user_demographic(user: User, event: Event) -> Demographic | None:
    """Get the demographic information for a user in a specific event.

    Args:
        user: The user object
        event: The event object

    Returns:
        demographic: The demographic information if registered, None if not.
    """
    demographic = Demographic.find_by_user_and_event(user.id, event.id)

    return demographic
