"""
Admin announcement management
"""

from ...core.exceptions import ValidationError

from ..models import (
    Announcement,
    AnnouncementType,
)
from ..services import AnnouncementService


def send_announcement(
    title: str,
    message: str,
    sender_id: int,
    expires_at: str | None = None,
    send_notification: bool = False,
) -> Announcement | None:
    """
    Send system wide announcement
    """
    return AnnouncementService.send_system_announcement(
        title = title,
        message = message,
        sender_id = sender_id,
        expires_at = expires_at,
        send_notification = send_notification,
    )


def send_event_announcement(
    event_id: int,
    title: str,
    message: str,
    announcement_type: str,
    sender_id: int,
    expires_at: str | None = None,
    send_notification: bool = False,
) -> Announcement:
    """
    Send announcement to event participants
    """
    try:
        type_enum = AnnouncementType(announcement_type)
    except ValueError as e:
        raise ValidationError(
            f"Invalid announcement type: {announcement_type}"
        ) from e

    return AnnouncementService.send_event_announcement(
        event_id=event_id,
        announcement_type=type_enum,
        title=title,
        message=message,
        sender_id=sender_id,
        expires_at=expires_at,
        send_notification=send_notification,
    )


def get_all_announcements() -> list[Announcement]:
    """
    Get all announcements (admin view).
    """
    return Announcement.get_all_announcements()


def delete_announcement(announcement: Announcement) -> None:
    """
    Delete announcement with notification cleanup
    """
    announcement.delete(commit = True)
