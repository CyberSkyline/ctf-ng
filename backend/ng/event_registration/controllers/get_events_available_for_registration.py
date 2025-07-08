from ...event_registration.models.EventRegistration import EventRegistration

def get_events_available_for_registration():
    """Retrieve all events that are available for registration.

    Returns:
        dict: A dictionary containing the success status and a list of events available for registration.
    """

    registrations = EventRegistration.get_events_available_for_registration()

    events = [registration.event for registration in registrations]


    return {
        "success": True,
        "events": events
    }