from ...core.utils.logger import get_logger
from ..models.Demographic import Demographic


logger = get_logger(__name__)

def get_user_demographic(user_id: int, event_id: int):
    """Get the demographic information for a user in a specific event.

    Args:
        user_id (int): The ID of the user.
        event_id (int): The ID of the event.

    Returns:
        dict: Success status and demographic data or error info.
    """

    demographic = Demographic.get_demographic_by_user_and_event(user_id, event_id)

    if not demographic:
        logger.warning(
            "User demographic not found",
            extra={"context": {"user_id": user_id, "event_id": event_id}},
        )
        return {
            "success": False,
            "error": f"No demographic data found for user ID {user_id} in event ID {event_id}",
        }

    return {
        "success": True,
        "demographic": demographic
    }