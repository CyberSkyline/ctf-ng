"""
Manage event lifecycle (start/end events)
"""

from ...models import Event
from ....notifications.services import NotificationService
from ....notifications.models import AnnouncementType

# TODO may need changes...
def start_event(event: Event) -> Event:
    """
    Manually start an event
    """
    event.start_event()

    NotificationService.send_event_announcement(
        event_id=event.id,
        announcement_type=AnnouncementType.EVENT_START,
        title=f"{event.name} Has Started!",
        message="The competition is now live. Good luck!",
        sender_id=None,
    )

    return event

# TODO may need changes...
def end_event(event: Event) -> Event:
    """
    Manually end an event
    """
    event.end_event()

    NotificationService.send_event_announcement(
        event_id=event.id,
        announcement_type=AnnouncementType.EVENT_END,
        title=f"{event.name} Has Ended",
        message="Thank you for participating!",
        sender_id=None,
    )

    return event
