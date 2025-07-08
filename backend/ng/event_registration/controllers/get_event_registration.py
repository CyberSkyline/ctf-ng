from ..models.EventRegistration import EventRegistration

def get_event_registration(event_id):
    """
    Get the event registration details for a specific event.
    
    Args:
        event_id (int): The ID of the event to retrieve registration details for.
    
    Returns:
        dict: A dictionary containing the event registration details.
    """

    event_registration = EventRegistration.get_event_registration_by_event_id(event_id)
    if not event_registration:
        return {"success": False, "error": "Event registration not found"}
    return {
        "success": True,
        "event_registration": event_registration
    }