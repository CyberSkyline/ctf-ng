from ..models.EventRegistration import EventRegistration
from ...core.utils.logger import get_logger

logger = get_logger(__name__)

def create_registration(event_id, public=False, reg_open=True, reg_start_date=None, reg_end_date=None):
    """Create a new event registration for the specified event.

    Args:
        event_id (int): The ID of the event to register for.
        reg_open (bool, optional): Whether the registration is open. Defaults to True.

    Returns:
        dict: A dictionary containing the success status and the created event registration.
    """

    try:
        registration = EventRegistration.create_event_registration(
            event_id=event_id,
            public=public,
            reg_open=reg_open,
            reg_start_date=reg_start_date,
            reg_end_date=reg_end_date
        )
        logger.info(
            "Event registration created successfully",
            extra={"context": {"event_id": event_id, "registration_id": registration.id}}
        )
        return {
            "success": True,
            "event_registration": registration
        }
    except Exception as e:
        logger.error(
            "Failed registration",
            extra={"context": {"event_id": event_id, "error": str(e)}}
        )
        return {
            "success": False,
            "error": str(e)
        }