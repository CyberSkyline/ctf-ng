from ..models.EventRegistration import EventRegistration
from datetime import datetime

def update_event_registration(event_id, data):

    event_registration = EventRegistration.get_event_registration_by_event_id(event_id)

    if not event_registration:
        return {"success": False, "error": "Event registration not found"}

    

    event_registration.update_registration(
        public=data.get("public"),
        reg_open=data.get("reg_open"),
        reg_start_date=datetime.strptime(data.get("reg_start_date"), "%Y-%m-%dT%H:%M:%S.%f") if data.get("reg_start_date") else None,
        reg_end_date=datetime.strptime(data.get("reg_end_date"), "%Y-%m-%dT%H:%M:%S.%f") if data.get("reg_end_date") else None
    )

    return {
        "success": True,
        "event_registration": event_registration
    }