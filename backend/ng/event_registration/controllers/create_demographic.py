from ..models.Demographic import Demographic
from CTFd.models import db

def create_demographic(user_id: int, event_id: int):
    """Create a demographic entry for a user in an event.

    Args:
        user_id (int): The user ID.
        event_id (int): The event ID.

    Returns:
        dict: Success status and demographic info or error info.
    """
    try:
        demographic = Demographic.create_demographic(
            user_id=user_id,
            event_id=event_id,
            reg_timestamp=db.func.now(),
        )
        return {
            "success": True,
            "demographic": demographic,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }